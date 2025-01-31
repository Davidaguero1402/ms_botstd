import threading
import time
import json
import logging
from datetime import datetime
from sqlalchemy.orm import scoped_session, sessionmaker
from ccxt import ExchangeError, NetworkError
from app import db  # Asegúrate de que esto use SQLAlchemy correctamente
from app.models import Bot, AuditoriaBot
from app.models.exchanges import Exchanges
from app.models.estrategias import Estrategias 
from app.models.activos import Activos
import ccxt
from app.models.operacionactiva import OperacionActiva

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TradingBot:
    def __init__(self, bot_id, db_session=None):
        self.bot_id = bot_id
        self.running = False
        self._stop_event = threading.Event()
        self.db_session = db_session or scoped_session(sessionmaker(bind=db.engine))  # Sesión por hilo
        self.bot = None
        self.exchange = None
        self.active_operation = None
        self.strategy_params = None
        self._load_bot_config()

    def _load_bot_config(self):
        """Carga configuración desde la DB con reintentos."""
        try:
            self.bot = self.db_session.query(Bot).get(self.bot_id)
            if not self.bot:
                raise ValueError(f"Bot {self.bot_id} no encontrado")

            exchange = self.db_session.query(Exchanges).get(self.bot.exchange_id)
            activo = self.db_session.query(Activos).get(self.bot.activo_id)
            estrategia = self.db_session.query(Estrategias).get(self.bot.estrategia_id)

            if not all([exchange, activo, estrategia]):
                raise ValueError("Configuración incompleta")

            self.exchange_config = exchange
            self.activo = activo
            self.strategy_params = json.loads(estrategia.parametros)

            self._init_exchange()

        except Exception as e:
            self._log_audit('ERROR', f"Error cargando configuración: {str(e)}")
            raise

    def _init_exchange(self):
        """Inicializa el exchange con manejo de errores."""
        try:
            exchange_class = getattr(ccxt, self.exchange_config.nombre.lower())
            self.exchange = exchange_class({
                'apiKey': self.exchange_config.api_key,
                'secret': self.exchange_config.secret_key,
                'enableRateLimit': True,
                'options': {'adjustForTimeDifference': True}
            })
            self.exchange.load_markets()  # Precarga mercados
        except AttributeError:
            raise ValueError(f"Exchange {self.exchange_config.nombre} no soportado")
        except ExchangeError as e:
            self._log_audit('ERROR', f"Error inicializando exchange: {str(e)}")
            raise

    def _get_market_data(self):
        """Obtiene datos de mercado con reintentos."""
        max_retries = 3
        for _ in range(max_retries):
            try:
                symbol = f"{self.activo.simbolo}/USDT"
                ticker = self.exchange.fetch_ticker(symbol)
                ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=1)[0]
                return {
                    'price': ticker['last'],
                    'volume': ohlcv[5],
                    'timestamp': datetime.fromtimestamp(ohlcv[0] / 1000)
                }
            except NetworkError as e:
                logging.warning(f"Error de red: {str(e)}. Reintentando...")
                time.sleep(5)
            except Exception as e:
                self._log_audit('ERROR', f"Error obteniendo datos: {str(e)}")
                raise
        raise Exception("Máximo de reintentos alcanzado")

    def _execute_strategy(self, market_data):
        """Ejecuta la estrategia con lógica de posición."""
        try:
            if not self.active_operation:
                entry_threshold = self.strategy_params.get('entry_threshold', 0.01)
                if market_data['price'] <= self.strategy_params.get('entry_price') * (1 - entry_threshold):
                    return 'BUY', self.strategy_params.get('quantity', 1)
            else:
                take_profit = self.active_operation.take_profit
                stop_loss = self.active_operation.stop_loss
                if market_data['price'] >= take_profit or market_data['price'] <= stop_loss:
                    return 'CLOSE', self.active_operation.cantidad
            return None, None
        except Exception as e:
            self._log_audit('ERROR', f"Error en estrategia: {str(e)}")
            return None, None

    def _execute_trade(self, action, quantity):
        """Ejecuta órdenes con manejo de errores."""
        try:
            symbol = f"{self.activo.simbolo}/USDT"
            if action == 'BUY':
                order = self.exchange.create_market_buy_order(symbol, quantity)
                self.active_operation = OperacionActiva(
                    bot_id=self.bot_id,
                    cantidad=quantity,
                    precio_entrada=order['price'],
                    take_profit=order['price'] * (1 + self.strategy_params.get('take_profit', 0.02)),
                    stop_loss=order['price'] * (1 - self.strategy_params.get('stop_loss', 0.01))
                )
                self.db_session.add(self.active_operation)
            elif action == 'CLOSE':
                order = self.exchange.create_market_sell_order(symbol, quantity)
                self.db_session.delete(self.active_operation)
                self.active_operation = None
            self.db_session.commit()
            return order
        except Exception as e:
            self.db_session.rollback()
            self._log_audit('ERROR', f"Error ejecutando orden {action}: {str(e)}")
            raise

    def _log_audit(self, event_type, description, details=None):
        """Registra auditorías de forma segura."""
        try:
            audit = AuditoriaBot(
                bot_id=self.bot_id,
                fecha=datetime.utcnow(),
                tipo_evento=event_type,
                descripcion=description,
                datos=json.dumps(details) if details else None
            )
            self.db_session.add(audit)
            self.db_session.commit()
        except Exception as e:
            logging.error(f"Error registrando auditoría: {str(e)}")
            self.db_session.rollback()

    def stop(self):
        """Detiene el bot de manera segura."""
        self.running = False
        self._stop_event.set()
        self._log_audit('INFO', "Bot detenido")
        self.db_session.remove()  # Limpia la sesión de DB

    def run(self):
        """Bucle principal de ejecución."""
        self.running = True
        self._log_audit('INFO', "Bot iniciado")
        
        while self.running and not self._stop_event.is_set():
            try:
                market_data = self._get_market_data()
                action, quantity = self._execute_strategy(market_data)
                
                if action:
                    self._execute_trade(action, quantity)
                    self._log_audit('TRADE', f"Operación {action} ejecutada", {
                        'precio': market_data['price'],
                        'cantidad': quantity
                    })
                
                time.sleep(self.bot.intervalo)
            
            except Exception as e:
                self.running = False
                self._log_audit('ERROR', f"Error crítico: {str(e)}")
                raise