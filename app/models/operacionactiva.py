import enum
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db import Base  # Asegúrate que Base sea la instancia correcta de declarative_base()
from datetime import datetime

# Definición de Enums
class TipoOperacion(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class EstadoOperacion(str, enum.Enum):
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"
    CANCELADA = "CANCELADA"

class OperacionActiva(Base):
    __tablename__ = 'operaciones_activas'

    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=False)  # Nombre de tabla en minúscula
    precio_entrada = Column(Float, nullable=False)
    cantidad = Column(Float, nullable=False)
    fecha_entrada = Column(DateTime, default=datetime.utcnow, nullable=False)
    tipo_operacion = Column(Enum(TipoOperacion), nullable=False)  # Usa el Enum aquí
    take_profit = Column(Float)
    stop_loss = Column(Float)
    estado = Column(Enum(EstadoOperacion), nullable=False, default=EstadoOperacion.ACTIVA)  # Y aquí

    # Relación opcional
    bot = relationship("Bots", back_populates="operaciones_activas")