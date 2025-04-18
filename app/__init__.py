# app/__init__.py
from fastapi import FastAPI
from app.db import engine, SessionLocal, Base
from app.models.bot import Bot
from app.models.exchange import Exchange
from app.models.profile import Profile
from app.models.trade import Trade
from app.models.bot_audit_log import BotAuditLog

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.routes import routes_bots
app.include_router(routes_bots.router)