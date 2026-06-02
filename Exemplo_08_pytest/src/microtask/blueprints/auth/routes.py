"""Rotas de autenticação.

Suporta dois modos de login na mesma URL `/auth/login`:

1. Form HTML (sessão tradicional)
   -> usado pelas páginas do helpdesk via formulário POST.

2. JSON (API)
   -> quando `Content-Type: application/json`, retorna `{access_token, ...}`.
   -> usado por clientes que falam JWT.

Política de segurança importante:
  - E-mail inexistente e senha errada retornam o MESMO 401, sem detalhar.
    Diferenciar entrega informação para enumeração de e-mails válidos.
"""

from functools import wraps

from flask import (
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ...auth_jwt import gerar_token
from ...models import User
from . import bp


def login_required(view):
    """Protege rotas que exigem login via sessão (web)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@bp.before_app_request
def load_logged_user():
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id else None


@bp.route("/login", methods=["GET", "POST"])
def login():
    # Modo JSON (cliente API)
    if request.method == "POST" and request.is_json:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            # Mesma resposta para usuário inexistente e senha errada
            return jsonify({"error": "credenciais inválidas"}), 401

        token = gerar_token(user)
        return jsonify(
            {
                "access_token": token,
                "token_type": "Bearer",
                "user": {"id": user.id, "name": user.name, "role": user.role},
            }
        ), 200

    # Modo Web (formulário)
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("pages.home"))
        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth/login.html")


@bp.post("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))
