from flask import render_template, request, redirect, url_for, abort
from . import bp
from ...models import User
from ...extensions import db

@bp.get("/")
def lista():
    users = User.query.limit(50).all()
    return render_template("users/lista.html", users=users)

@bp.route("/criar-usuario", methods=["GET", "POST"])
def criar_usuario():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        role = request.form.get("role")

        novo_usuario = User(name=name, email=email, role=role)
        db.session.add(novo_usuario)
        db.session.commit()

        # Redireciona para a lista para evitar reenvio de formulário
        return redirect(url_for("users.lista"))

    return render_template("users/inserir_usuario.html")

@bp.get("/excluir-temporario")
def excluir_temporario():
    email_alvo = "temporario@campus.edu.br"
    usuario = User.query.filter_by(email=email_alvo).first()
    
    if not usuario:
        return f"Erro: Usuário {email_alvo} não encontrado.", 404
    
    db.session.delete(usuario)
    db.session.commit()
    return f"Usuário '{usuario.name}' removido com sucesso!"

@bp.get("/promover-teste")
def promover_teste():
    user = User.query.get(2)
    if not user:
        return "Erro: Usuário de ID 2 não encontrado.", 404
    
    user.role = "agent"
    db.session.commit()
    return f"O usuário {user.name} agora é um {user.role}."