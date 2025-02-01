from fastapi import FastAPI
from app.models.bot import Bot
from app.db import engine, SessionLocal, Base
from app.models.activos import Activos
from app.models.bot import Bot
from app.models.auditoriabot import AuditoriaBot
from app.models.estrategias import Estrategias
from app.models.exchanges import Exchanges
from app.models.operacionactiva import OperacionActiva
from app.models.operaciones import Operaciones

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