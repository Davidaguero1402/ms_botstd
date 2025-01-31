from app import Base as db

class Activos(db.Model):
    __tablename__ = 'Activos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120))
    simbolo = db.Column(db.String(10))
    tipo = db.Column(db.String(50))

    operaciones = db.relationship('Operaciones', backref='activo', lazy=True)
    