from app import Base as db
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

class OperacionActiva(db):
    __tablename__ = 'operaciones_activas'
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('Bots.id'), nullable=False)
    precio_entrada = Column(Float, nullable=False)
    cantidad = Column(Float, nullable=False)
    fecha_entrada = Column(DateTime, nullable=False)
    tipo_operacion = Column(String(10), nullable=False)  # LONG o SHORT
    take_profit = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    estado = Column(String(20), nullable=False)  # ACTIVA, CERRADA, CANCELADA
