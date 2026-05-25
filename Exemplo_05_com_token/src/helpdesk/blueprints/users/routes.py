from flask import flash, redirect, render_template, request, url_for

from . import bp
from ...extensions import db
from ...models import User
from ..auth.routes import login_required


@bp.get("/")
@login_required
def lista():
    users = User.query.order_by(User.name.asc()).limit(50).all()
    return render_template("users/lista.html", users=users)


@bp.route("/criar-usuario", methods=["GET", "POST"])
@login_required
def criar_usuario():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role")
        password = request.form.get("password", "")

        if User.query.filter_by(email=email).first():
            flash("Já existe um usuário com este e-mail.", "danger")
            return render_template("users/inserir_usuario.html")

        novo_usuario = User(name=name, email=email, role=role)
        novo_usuario.set_password(password)

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Usuário criado com senha protegida por hash.", "success")
        return render_template("users/criar_usuario.html", user=novo_usuario)

    return render_template("users/inserir_usuario.html")
