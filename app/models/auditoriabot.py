from app import Base as db

class AuditoriaBot(db.Model):
    __tablename__ = 'auditoria_bot'
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('Bots.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    datos = db.Column(db.Text, nullable=True)