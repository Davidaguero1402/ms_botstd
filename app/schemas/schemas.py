from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from app.models import BotStatus

class BotConfig(BaseModel):
    risk_percentage: float
    max_position_size: float
    strategy_params: Dict

class BotCreate(BaseModel):
    name: str
    strategy: str
    exchange_id: str
    symbol: str
    config: BotConfig

class BotUpdate(BaseModel):
    name: Optional[str] = None
    strategy: Optional[str] = None
    exchange_id: Optional[str] = None
    symbol: Optional[str] = None
    config: Optional[BotConfig] = None

class BotInDB(BotCreate):
    id: int
    status: BotStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BotStatus(BaseModel):
    status: BotStatus
    current_position: Dict
    last_update: datetime
    error: Optional[str] = None

class BotPerformance(BaseModel):
    total_trades: int
    win_rate: float
    profit_loss: float
    sharpe_ratio: float

