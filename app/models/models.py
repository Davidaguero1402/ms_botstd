from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class BotStatus(enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    strategy = Column(String)
    exchange_id = Column(String)
    symbol = Column(String)
    config = Column(JSON)
    status = Column(Enum(BotStatus), default=BotStatus.IDLE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

