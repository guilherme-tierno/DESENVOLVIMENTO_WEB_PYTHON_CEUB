from . extensions import db
from . models import Aluno, Campus

def register_routes(app):

    @app.route("/")
    def home():
        return "API simples - Aluno e Campus"

    # -------- INIT DB --------
    @app.route("/init")
    def init_db():
        db.create_all()
        return "Banco criado!"

    # CREATE campus
    @app.route("/create-campus/<nome>")
    def create_campus(nome):
        campus = Campus(nome=nome)
        db.session.add(campus)
        db.session.commit()
        return f"Campus {campus.nome} criado!"

    # LIST campus
    @app.route("/campus")
    def list_campus():
        campus_list = Campus.query.all()
        return "<br>".join([f"{c.id} - {c.nome}" for c in campus_list])

    # CREATE aluno
    @app.route("/create-aluno/<nome>/<int:campus_id>")
    def create_aluno(nome, campus_id):
        campus = Campus.query.get(campus_id)
        if not campus:
            return "Campus não encontrado"
        aluno = Aluno(nome=nome, campus_id=campus_id)
        db.session.add(aluno)
        db.session.commit()
        return f"Aluno {aluno.nome} criado no campus {campus.nome}"

    # LIST alunos
    @app.route("/alunos")
    def list_alunos():
        alunos = Aluno.query.all()
        resultado = ""
        for a in alunos:
            resultado += f"{a.id} - {a.nome} (Campus: {a.campus_id})<br>"
        return resultado

    # UPDATE aluno
    @app.route("/update-aluno/<int:id>/<novo_nome>")
    def update_aluno(id, novo_nome):
        aluno = Aluno.query.get(id)
        if not aluno:
            return "Aluno não encontrado"
        aluno.nome = novo_nome
        db.session.commit()
        return "Aluno atualizado!"

    # DELETE aluno
    @app.route("/delete-aluno/<int:id>")
    def delete_aluno(id):
        aluno = Aluno.query.get(id)
        if not aluno:
            return "Aluno não encontrado"
        db.session.delete(aluno)
        db.session.commit()
        return "Aluno deletado!"