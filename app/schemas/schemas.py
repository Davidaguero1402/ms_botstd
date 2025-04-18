# app/schemas/schemas.py
from pydantic import BaseModel
from typing import Dict, Optional, Any
from datetime import datetime
import uuid

class BotConfig(BaseModel):
    risk_percentage: float
    max_position_size: float
    strategy_params: Dict[str, Any]

class ExchangeCreate(BaseModel):
    name: str
    api_key: str
    api_secret: str
    user_id: uuid.UUID

class ExchangeInDB(ExchangeCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ProfileCreate(BaseModel):
    display_name: str
    email: str

class ProfileInDB(ProfileCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class BotCreate(BaseModel):
    name: str
    strategy: str
    exchange_id: uuid.UUID
    user_id: uuid.UUID
    symbol: str
    config: Dict[str, Any]

class BotUpdate(BaseModel):
    name: Optional[str] = None
    strategy: Optional[str] = None
    exchange_id: Optional[uuid.UUID] = None
    symbol: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class BotInDB(BaseModel):
    id: uuid.UUID
    name: str
    strategy: str
    exchange_id: uuid.UUID
    user_id: uuid.UUID
    symbol: str
    config: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class TradeCreate(BaseModel):
    bot_id: uuid.UUID
    symbol: str
    side: str
    amount: float
    price: float
    status: str = "open"

class TradeInDB(BaseModel):
    id: uuid.UUID
    bot_id: uuid.UUID
    symbol: str
    side: str
    amount: float
    price: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class BotAuditLogCreate(BaseModel):
    bot_id: uuid.UUID
    event_type: str
    description: str
    data: Optional[Dict[str, Any]] = None

class BotAuditLogInDB(BaseModel):
    id: uuid.UUID
    bot_id: uuid.UUID
    event_type: str
    description: str
    data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class BotStatus(BaseModel):
    status: str
    current_position: Dict[str, Any]
    last_update: datetime
    error: Optional[str] = None

class BotPerformance(BaseModel):
    total_trades: int
    win_rate: float
    profit_loss: float
    sharpe_ratio: float