import ccxt
from ccxt.base.errors import ExchangeError

class ExchangeFactory:
    @staticmethod
    def create_exchange(exchange_name, api_key, secret_key):
        try:
            # Determinar la clase de exchange basada en el nombre de la plataforma
            # Por ejemplo, 'bingx' -> 'bingx'
            exchange_class_name = exchange_name.lower()
            
            exchange_class = getattr(ccxt, exchange_class_name)
            exchange = exchange_class({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {'adjustForTimeDifference': True}
            })
            exchange.load_markets()  # Precarga mercados
            return exchange
        except AttributeError:
            raise ValueError(f"Exchange {exchange_name} no soportado")
        except ExchangeError as e:
            raise ValueError(f"Error inicializando exchange: {str(e)}")