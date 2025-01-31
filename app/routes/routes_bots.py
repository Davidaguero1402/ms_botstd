from app import app, schemas, models
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import get_db
from datetime import datetime
from typing import List
from fastapi import APIRouter
from app.models.models import Bot
from app.schemas.schemas import BotInDB
from app.utils import bot_manager

router = APIRouter(prefix="/api/v1/bots", tags=["bots"])

@router.post("/", response_model=schemas.BotInDB)
def create_bot(bot: schemas.BotCreate, db: Session = Depends(get_db)):
    db_bot = models.Bot(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

@router.get("/", response_model=List[schemas.BotInDB])
def list_bots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bots = db.query(models.Bot).offset(skip).limit(limit).all()
    return bots

@router.get("/{bot_id}", response_model=schemas.BotInDB)
def get_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

@router.put("/{bot_id}", response_model=schemas.BotInDB)
def update_bot(bot_id: int, bot: schemas.BotUpdate, db: Session = Depends(get_db)):
    db_bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if db_bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    update_data = bot.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bot, key, value)
    
    db_bot.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_bot)
    return db_bot

@router.delete("/{bot_id}", response_model=schemas.BotInDB)
def delete_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    db.delete(bot)
    db.commit()
    return bot

# Para /start (versión definitiva)
@router.post("/{bot_id}/start", response_model=schemas.BotInDB)
def start_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Inicia el bot en un hilo
    bot_manager.start_bot(bot_id)  # <-- Key: Ejecuta el TradingBot
    
    # Actualiza el estado en la DB
    bot.status = models.BotStatus.RUNNING
    db.commit()
    db.refresh(bot)
    
    return bot

# Para /stop (versión definitiva)
@router.post("/{bot_id}/stop", response_model=schemas.BotInDB)
def stop_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Detén el bot
    bot_manager.stop_bot(bot_id)  # <-- Key: Detiene el TradingBot
    
    # Actualiza el estado en la DB
    bot.status = models.BotStatus.STOPPED
    db.commit()
    db.refresh(bot)
    
    return bot

@router.post("/{bot_id}/stop", response_model=BotInDB)
def stop_bot(
    bot_id: int,
    db: Session = Depends(get_db),
):
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Detén el bot (implementa lógica de parada en TradingBot si es necesario)
    bot_manager.stop_bot(bot_id)
    
    # Actualiza el estado en la base de datos
    bot.status = "stopped"
    db.commit()
    
    return bot

@router.get("/{bot_id}/status", response_model=schemas.BotStatus)
def get_bot_status(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    # Here you would typically fetch the current position and other status details from your trading system
    return schemas.BotStatus(
        status=bot.status,
        current_position={},  # Placeholder, replace with actual data
        last_update=bot.updated_at,
        error=None
    )

@router.get("/{bot_id}/trades")
def get_bot_trades(bot_id: int, start_date: datetime = None, end_date: datetime = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    # This would typically involve querying a time series database or a trades table
    # For this example, we'll just return a placeholder
    return {"message": "Trade history would be returned here"}

@router.get("/{bot_id}/performance", response_model=schemas.BotPerformance)
def get_bot_performance(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    # Here you would typically calculate these metrics based on the bot's trade history
    return schemas.BotPerformance(
        total_trades=100,  # Placeholder
        win_rate=0.6,  # Placeholder
        profit_loss=1000.0,  # Placeholder
        sharpe_ratio=1.5  # Placeholder
    )

@router.get("/{bot_id}/logs")
def get_bot_logs(bot_id: int, level: str = None, start_date: datetime = None, end_date: datetime = None, limit: int = 100, db: Session = Depends(get_db)):
    # This would typically involve querying a logging system
    # For this example, we'll just return a placeholder
    return {"message": "Bot logs would be returned here"}
