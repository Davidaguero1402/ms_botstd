from fastapi import FastAPI
from app.models import models
from app.db import engine, SessionLocal, Base


models.Base.metadata.create_all(bind=engine)

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