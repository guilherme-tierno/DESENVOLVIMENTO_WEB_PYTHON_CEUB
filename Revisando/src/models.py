from . extensions import db

class Campus(db.Model):
    __tablename__ = "tb_campus"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    # relação: um campus tem vários alunos
    alunos = db.relationship("Aluno", backref="tb_campus", lazy=True)


class Aluno(db.Model):
    __tablename__ = "tb_alunos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)

    # chave estrangeira: aluno pertence a um campus
    campus_id = db.Column(
        db.Integer,
        db.ForeignKey("tb_campus.id"),
        nullable=False
    )