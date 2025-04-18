# app/utils/trading_bot.py
import threading
import time
import json
import logging
from datetime import datetime
from sqlalchemy.orm import scoped_session, sessionmaker
from ccxt import ExchangeError, NetworkError
from app.db.database import engine
from app.models.bot import Bot
from app.models.exchange import Exchange
from app.models.trade import Trade
from app.models.bot_audit_log import BotAuditLog
import ccxt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TradingBot:
    def __init__(self, bot_id, db_session=None):
        self.bot_id = bot_id
        self.running = False
        self._stop_event = threading.Event()
        self.db_session = db_session or scoped_session(sessionmaker(bind=engine))  # Sesión por hilo
        self.bot = None
        self.exchange = None
        self.active_trade = None
        self.strategy_params = None
        self._load_bot_config()

    def _load_bot_config(self):
        """Carga configuración desde la DB con reintentos."""
        try:
            self.bot = self.db_session.query(Bot).get(self.bot_id)
            if not self.bot:
                raise ValueError(f"Bot {self.bot_id} no encontrado")

            exchange = self.db_session.query(Exchange).get(self.bot.exchange_id)
            if not exchange:
                raise ValueError("Exchange no encontrado")

            self.exchange_config = exchange
            self.strategy_params = self.bot.config.get('strategy_params', {})

            self._init_exchange()

        except Exception as e:
            self._log_audit('ERROR', f"Error cargando configuración: {str(e)}")
            raise

    def _init_exchange(self):
        """Inicializa el exchange con manejo de errores."""
        try:
            exchange_class = getattr(ccxt, self.exchange_config.name.lower())
            self.exchange = exchange_class({
                'apiKey': self.exchange_config.api_key,
                'secret': self.exchange_config.api_secret,
                'enableRateLimit': True,
                'options': {'adjustForTimeDifference': True}
            })
            self.exchange.load_markets()  # Precarga mercados
        except AttributeError:
            raise ValueError(f"Exchange {self.exchange_config.name} no soportado")
        except ExchangeError as e:
            self._log_audit('ERROR', f"Error inicializando exchange: {str(e)}")
            raise

    def _get_market_data(self):
        """Obtiene datos de mercado con reintentos."""
        max_retries = 3
        for _ in range(max_retries):
            try:
                symbol = self.bot.symbol
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
            # Buscar operaciones activas
            active_trade = self.db_session.query(Trade).filter(
                Trade.bot_id == self.bot_id,
                Trade.status == 'open'
            ).first()
            
            self.active_trade = active_trade
            
            # Lógica simplificada de estrategia como ejemplo
            if not active_trade:
                entry_threshold = self.strategy_params.get('entry_threshold', 0.01)
                entry_price = self.strategy_params.get('entry_price', market_data['price'])
                
                if market_data['price'] <= entry_price * (1 - entry_threshold):
                    return 'buy', self.strategy_params.get('quantity', 1)
            else:
                take_profit = float(active_trade.price) * (1 + self.strategy_params.get('take_profit', 0.02))
                stop_loss = float(active_trade.price) * (1 - self.strategy_params.get('stop_loss', 0.01))
                
                if market_data['price'] >= take_profit or market_data['price'] <= stop_loss:
                    return 'sell', float(active_trade.amount)
                    
            return None, None
        except Exception as e:
            self._log_audit('ERROR', f"Error en estrategia: {str(e)}")
            return None, None

    def _execute_trade(self, action, quantity):
        """Ejecuta órdenes con manejo de errores."""
        try:
            symbol = self.bot.symbol
            
            if action == 'buy':
                order = self.exchange.create_market_buy_order(symbol, quantity)
                
                # Crear un nuevo trade
                trade = Trade(
                    bot_id=self.bot_id,
                    symbol=symbol,
                    side='buy',
                    amount=quantity,
                    price=order['price'],
                    status='open'
                )
                self.db_session.add(trade)
                
            elif action == 'sell':
                order = self.exchange.create_market_sell_order(symbol, quantity)
                
                # Cerrar el trade activo
                if self.active_trade:
                    self.active_trade.status = 'closed'
                    self.active_trade.updated_at = datetime.utcnow()
                
            self.db_session.commit()
            return order
        except Exception as e:
            self.db_session.rollback()
            self._log_audit('ERROR', f"Error ejecutando orden {action}: {str(e)}")
            raise

    def _log_audit(self, event_type, description, details=None):
        """Registra auditorías de forma segura."""
        try:
            audit = BotAuditLog(
                bot_id=self.bot_id,
                event_type=event_type,
                description=description,
                data=details
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
                
                # Intervalo de verificación (usar el del config o un default)
                interval = self.bot.config.get('interval', 60)  
                time.sleep(interval)
            
            except Exception as e:
                self.running = False
                self._log_audit('ERROR', f"Error crítico: {str(e)}")
                raise