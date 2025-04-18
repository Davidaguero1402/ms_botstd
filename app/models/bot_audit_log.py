# app/models/bot_audit_log.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base

class BotAuditLog(Base):
    __tablename__ = 'bot_audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(UUID(as_uuid=True), ForeignKey('bots.id'), nullable=False)
    event_type = Column(String, nullable=False)  # Renombrado de tipo_evento
    description = Column(Text, nullable=False)  # Renombrado de descripcion
    data = Column(JSONB)  # Cambiado de Text a JSONB, más coherente con Supabase
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relaciones
    bot = relationship("Bot", back_populates="audit_logs")

