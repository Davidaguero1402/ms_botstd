from app.db.database import Base as db
from sqlalchemy import Column, Integer, String, Text

class Estrategias(db):
    __tablename__ = 'estrategias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120))
    descripcion = Column(Text)
    parametros = Column(Text)