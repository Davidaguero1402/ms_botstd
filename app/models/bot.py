from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
import enum
from time import time
from app.db.database import Base


class BotStatus(enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    strategy = Column(String)
    exchange_id = Column(Integer)
    symbol = Column(String)
    config = Column(JSON)
    status = Column(Enum(BotStatus), default=BotStatus.IDLE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    operaciones_activas = relationship("OperacionActiva", back_populates="bot")  # Relación a operaciones activas
    operaciones = relationship("Operaciones", back_populates="bot")  # Relación a historial de operaciones