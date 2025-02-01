from app import Base as db
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey

class AuditoriaBot(db):
    __tablename__ = 'auditoria_bot'
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=False)
    fecha = Column(DateTime, nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    datos = Column(Text, nullable=True)