# app/models/bot.py
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
import enum
import uuid
from app.db.database import Base


class BotStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class Bot(Base):
    __tablename__ = "bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    strategy = Column(String)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey('exchanges.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    symbol = Column(String)
    config = Column(JSON)  # Se cambiará a JSONB en la migración SQL
    status = Column(String, default="active")  # Usamos String en lugar de Enum para compatibilidad
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    exchange = relationship("Exchange", back_populates="bots")
    user = relationship("Profile", back_populates="bots")
    trades = relationship("Trade", back_populates="bot")
    audit_logs = relationship("BotAuditLog", back_populates="bot")

