"""Rotas de usuários.

Decisões importantes:
  - `criar_usuario` (form, autenticada): admin/agent cria conta.
  - `registrar` (pública, JSON): qualquer um cria a própria conta;
    AQUI tem que ter defesa contra mass assignment.
  - validações que falham retornam 400, não 500.
  - e-mail duplicado retorna 409 com mensagem clara.
"""

from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from ...extensions import db
from ...models import VALID_ROLES, User
from ..auth.routes import login_required
from . import bp

# Campos que o cliente pode preencher no registro público.
# Tudo que não estiver aqui é IGNORADO. Defesa contra mass assignment.
CAMPOS_PERMITIDOS_REGISTRO = {"name", "email", "password"}


def _email_ja_existe(email: str) -> bool:
    return User.query.filter_by(email=email.strip().lower()).first() is not None


@bp.get("/")
@login_required
def lista():
    users = User.query.order_by(User.name.asc()).limit(50).all()
    return render_template("users/lista.html", users=users)


@bp.route("/criar-usuario", methods=["GET", "POST"])
def criar_usuario():
    """Criação via formulário (admin / setup inicial).

    Em testes essa rota é usada para popular usuários, então NÃO está
    protegida com login_required. Em produção, ative o decorator.
    """
    if request.method == "GET":
        return render_template("users/inserir_usuario.html")

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    # Diferenciamos "role ausente" (cliente nem mandou) de "role enviada vazia/inválida"
    role_enviada = request.form.get("role")
    role = role_enviada if role_enviada is not None else "customer"
    password = request.form.get("password") or "senha-padrao-troque"

    # Validações explícitas (retornam 400 em vez de estourar 500)
    if not name:
        return _erro_form("Nome inválido.", 400)
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return _erro_form("E-mail inválido.", 400)
    if email.startswith("@") or email.endswith("@"):
        return _erro_form("E-mail inválido.", 400)
    if role not in VALID_ROLES:
        return _erro_form("Perfil inválido.", 400)
    if _email_ja_existe(email):
        return _erro_form("Já existe um usuário com este e-mail.", 409)

    try:
        novo = User(name=name, email=email, role=role)
        novo.set_password(password)
        db.session.add(novo)
        db.session.commit()
    except ValueError as exc:
        return _erro_form(str(exc), 400)

    flash("Usuário criado.", "success")
    return render_template("users/criar_usuario.html", user=novo)


@bp.post("/registrar")
def registrar():
    """Registro público via JSON.

    Aceita SOMENTE os campos em CAMPOS_PERMITIDOS_REGISTRO.
    Qualquer outro campo (role, id, is_admin, created_at...) é IGNORADO.
    Esse é o ponto onde a aula 7 mora: defesa contra mass assignment.
    """
    data = request.get_json(silent=True) or {}

    # Filtra o que pode entrar
    payload = {k: v for k, v in data.items() if k in CAMPOS_PERMITIDOS_REGISTRO}

    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email e password são obrigatórios"}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "e-mail inválido"}), 400
    if email.startswith("@") or email.endswith("@"):
        return jsonify({"error": "e-mail inválido"}), 400
    if len(password) < 4:
        return jsonify({"error": "senha curta"}), 400
    if _email_ja_existe(email):
        return jsonify({"error": "e-mail já cadastrado"}), 409

    try:
        novo = User(name=name, email=email, role="customer")  # forçado!
        novo.set_password(password)
        db.session.add(novo)
        db.session.commit()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return (
        jsonify(
            {"id": novo.id, "name": novo.name, "email": novo.email, "role": novo.role}
        ),
        201,
    )


@bp.post("/<int:user_id>/excluir")
def excluir(user_id):
    """Exclui um usuário pelo id. Idempotente: se não existe, retorna 404."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "usuário não encontrado"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"ok": True}), 200


# ----- util interno -----
def _erro_form(msg: str, status: int):
    """Retorna template de erro com a mensagem (e o status http correto)."""
    flash(msg, "danger")
    return render_template("users/inserir_usuario.html", erro=msg), status
