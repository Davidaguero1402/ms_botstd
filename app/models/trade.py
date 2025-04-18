# app/models/trade.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(UUID(as_uuid=True), ForeignKey('bots.id'))
    symbol = Column(String)
    side = Column(String)  # Equivalente a tipo_operacion pero con nombres de columna de Supabase
    amount = Column(Numeric)  # Equivalente a cantidad
    price = Column(Numeric)
    status = Column(String)  # Equivalente a estado
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    bot = relationship("Bot", back_populates="trades")

