import threading
import time
import json
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from ccxt import ExchangeError
from app import db
from models import Bots, Exchanges, Activos, Estrategias, AuditoriaBot, OperacionActiva
import ccxt

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TradingBot:
    def __init__(self, bot_id):
        self.bot_id = bot_id
        self.running = False
        self.bot = None
        self.exchange = None
        self.active_operation = None
        self.strategy_params = None
        self.load_bot_config()
        self.load_exchange()

    def load_bot_config(self):
        """Carga la configuración del bot desde la base de datos."""
        try:
            self.bot = Bots.query.get(self.bot_id)
            if not self.bot:
                raise ValueError(f"Bot con ID {self.bot_id} no encontrado.")

            # Cargar configuraciones adicionales
            exchange = Exchanges.query.get(self.bot.exchange_id)
            activo = Activos.query.get(self.bot.activo_id)
            estrategia = Estrategias.query.get(self.bot.estrategia_id)

            if not exchange or not activo or not estrategia:
                raise ValueError("Error al cargar configuraciones del bot.")

            self.exchange_config = exchange
            self.activo = activo
            self.strategy_params = json.loads(estrategia.parametros)
        except Exception as e:
            logging.error(f"Error al cargar configuración del bot: {str(e)}")
            raise

    def load_exchange(self):
        """Inicializa el cliente del exchange."""
        try:
            exchange_class = getattr(ccxt, self.exchange_config.nombre.lower())
            self.exchange = exchange_class({
                'apiKey': self.exchange_config.api_key,
                'secret': self.exchange_config.secret_key,
                'enableRateLimit': True
            })
        except ExchangeError as e:
            logging.error(f"Error al inicializar exchange: {str(e)}")
            raise

    def get_market_data(self):
        """Obtiene datos de mercado del activo configurado."""
        try:
            symbol = f"{self.activo.simbolo}/USDT"
            ticker = self.exchange.fetch_ticker(symbol)
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=1)[0]
            return {
                'price': ticker['last'],
                'volume': ohlcv[5],
                'timestamp': datetime.fromtimestamp(ohlcv[0] / 1000)
            }
        except Exception as e:
            logging.error(f"Error al obtener datos de mercado: {str(e)}")
            self.log_audit('ERROR', 'Error al obtener datos de mercado', {'error': str(e)})
            raise

    def apply_strategy(self, market_data):
        """Aplica la estrategia del bot para determinar acciones."""
        # Ejemplo básico: Compra si el precio baja un 1% del precio anterior
        # (El detalle dependerá de la lógica de la estrategia configurada).
        if self.active_operation is None:
            price_threshold = market_data['price'] * (1 - self.strategy_params.get('entry_threshold', 0.01))
            if market_data['price'] <= price_threshold:
                return 'BUY', 1  # Abrir posición LONG
        else:
            # Verificar si se cumple Take Profit o Stop Loss
            if market_data['price'] >= self.active_operation.take_profit or \
               market_data['price'] <= self.active_operation.stop_loss:
                return 'CLOSE', None
        return None, None

    def execute_trade(self, order_type, quantity):
        """Ejecuta una operación en el exchange."""
        try:
            symbol = f"{self.activo.simbolo}/USDT"
            if order_type == 'BUY':
                order = self.exchange.create_market_buy_order(symbol, quantity)
            elif order_type == 'SELL':
                order = self.exchange.create_market_sell_order(symbol, quantity)
            else:
                raise ValueError("Tipo de orden no reconocido.")
            return order
        except Exception as e:
            logging.error(f"Error al ejecutar orden {order_type}: {str(e)}")
            self.log_audit('ERROR', f"Error al ejecutar orden {order_type}", {'error': str(e)})
            raise

    def log_audit(self, event_type, description, details=None):
        """Registra eventos de auditoría en la base de datos."""
        try:
            audit = AuditoriaBot(
                bot_id=self.bot_id,
                fecha=datetime.utcnow(),
                tipo_evento=event_type,
                descripcion=description,
                datos=json.dumps(details) if details else None
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            logging.error(f"Error al registrar auditoría: {str(e)}")
            db.session.rollback()

    def run(self):
        """Inicia la lógica continua del bot."""
        self.running = True
        self.log_audit('INFO', "Bot iniciado")
        while self.running:
            try:
                market_data = self.get_market_data()
                action, quantity = self.apply_strategy(market_data)
                if action == 'BUY':
                    self.execute_trade('BUY', quantity)
                    self.log_audit('TRADE', 'Operación de compra ejecutada', market_data)
                elif action == 'CLOSE':
                    self.execute_trade('SELL', self.active_operation.cantidad)
                    self.log_audit('TRADE', 'Operación cerrada', market_data)
                time.sleep(self.bot.intervalo)
            except Exception as e:
                logging.error(f"Error en la ejecución del bot: {str(e)}")
                self.log_audit('ERROR', 'Error en la ejecución del bot', {'error': str(e)})
