from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Activos(Base):
    __tablename__ = 'Activos'  # Nombre de tabla en minúscula
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120))
    simbolo = Column(String(10))
    tipo = Column(String(50))

    # Relación (asegúrate que el modelo Operaciones existe)
    operaciones = relationship('Operaciones', back_populates='Activo')