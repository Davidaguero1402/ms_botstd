from app.db.database import Base as db
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship

class Operaciones(db):
    __tablename__ = 'operaciones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=False)
    activo_id = Column(Integer, ForeignKey('activos.id'), nullable=False)
    tipo_operacion = Column(String(50))
    precio = Column(Float)
    cantidad = Column(Float)
    fecha = Column(DateTime)

    # Relaciones
    activo = relationship("Activos", back_populates="operaciones")  # Nombre en minúscula
    bot = relationship("Bot", back_populates="operaciones")
