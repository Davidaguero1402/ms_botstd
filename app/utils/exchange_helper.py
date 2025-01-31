import ccxt

class ExchangeHelper:
    def __init__(self,id, exchange_name, api_key, secret_key):
        self.id = id
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.secret_key = secret_key
        self.exchange = self.initialize_exchange()

    def initialize_exchange(self):
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            return exchange_class({
                'apiKey': self.api_key,
                'secret': self.secret_key,
                'enableRateLimit': True,
            })
        except AttributeError:
            raise ValueError(f"Exchange '{self.exchange_name}' is not supported by ccxt.")

    def get_market_data(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1m', limit=10)  # Últimos 10 minutos
            return {
                'ticker': ticker,
                'ohlcv': ohlcv,
            }
        except Exception as e:
            raise RuntimeError(f"Error fetching market data: {e}")

    def create_order(self, symbol, order_type, side, amount, price=None):
        try:
            if order_type == 'limit':
                return self.exchange.create_limit_order(symbol, side, amount, price)
            elif order_type == 'market':
                return self.exchange.create_market_order(symbol, side, amount)
            else:
                raise ValueError("Invalid order type. Use 'limit' or 'market'.")
        except Exception as e:
            raise RuntimeError(f"Error creating order: {e}")

    def get_balance(self):
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            raise RuntimeError(f"Error fetching balance: {e}")

    def cancel_order(self, order_id, symbol):
        try:
            return self.exchange.cancel_order(order_id, symbol)
        except Exception as e:
            raise RuntimeError(f"Error canceling order: {e}")