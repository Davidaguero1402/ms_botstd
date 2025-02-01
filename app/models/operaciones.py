from app.db.database import Base as db
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime

class Operaciones(db):
    __tablename__ = 'Operaciones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(Integer, ForeignKey('Bots.id'), nullable=False)
    activo_id = Column(Integer, ForeignKey('Activos.id'), nullable=False)
    tipo_operacion = Column(String(50))
    precio = Column(Float)
    cantidad = Column(Float)
    fecha = Column(DateTime)