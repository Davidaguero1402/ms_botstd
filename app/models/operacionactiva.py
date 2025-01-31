from app import Base as db

class OperacionActiva(db.Model):
    __tablename__ = 'operaciones_activas'
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('Bots.id'), nullable=False)
    precio_entrada = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    fecha_entrada = db.Column(db.DateTime, nullable=False)
    tipo_operacion = db.Column(db.String(10), nullable=False)  # LONG o SHORT
    take_profit = db.Column(db.Float, nullable=True)
    stop_loss = db.Column(db.Float, nullable=True)
    estado = db.Column(db.String(20), nullable=False)  # ACTIVA, CERRADA, CANCELADA
