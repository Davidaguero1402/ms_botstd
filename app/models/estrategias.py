from app import Base as db

class Estrategias(db.Model):
    __tablename__ = 'Estrategias'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120))
    descripcion = db.Column(db.Text)
    parametros = db.Column(db.Text)