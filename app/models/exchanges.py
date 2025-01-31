from app import Base as db

class Exchanges(db.Model):
    __tablename__ = 'Exchanges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120))
    api_key = db.Column(db.String(255))
    secret_key = db.Column(db.String(255))

    def fetch_margin_balance(self):
        # Implementación del método
        pass

    def create_margin_order(self, symbol, type, side, amount, price):
        # Implementación del método
        pass

    def fetch_index_ohlcv(self, symbol, timeframe):
        # Implementación del método
        pass

    def fetch_funding_rate(self, symbol):
        # Implementación del método
        pass

    def watch_ticker(self, symbol):
        # Implementación del método
        pass