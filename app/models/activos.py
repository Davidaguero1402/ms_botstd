from app import Base as db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Activos(db):
    __tablename__ = 'Activos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120))
    simbolo = Column(String(10))
    tipo = Column(String(50))

    operaciones = relationship('Operaciones', backref='activo', lazy=True)
    