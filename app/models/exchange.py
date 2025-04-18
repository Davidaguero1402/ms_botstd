# app/models/exchange.py
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base

class Exchange(Base):
    __tablename__ = 'exchanges'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    api_key = Column(String)
    api_secret = Column(String)  # Renombrado de secret_key a api_secret
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("Profile", back_populates="exchanges")
    bots = relationship("Bot", back_populates="exchange")
    
    # Métodos heredados de la clase anterior
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
