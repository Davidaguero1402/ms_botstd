from app.db.database import Base as db
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey

class AuditoriaBot(db):
    __tablename__ = 'Auditoria_bot'
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('Bots.id'), nullable=False)
    fecha = Column(DateTime, nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    datos = Column(Text, nullable=True)