"""Rotas de tickets (web)."""

from flask import (
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from ...extensions import db
from ...models import Ticket, User
from ..auth.routes import login_required
from . import bp


@bp.get("/")
def lista():
    """Listagem aberta — facilita rodar testes simples sem precisar logar."""
    tickets = (
        Ticket.query.order_by(Ticket.created_at.desc(), Ticket.id.desc()).all()
    )
    return render_template("tickets/lista.html", tickets=tickets)


@bp.get("/<int:ticket_id>")
def detalhe(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        abort(404)
    return render_template("tickets/detalhe.html", ticket=ticket)


@bp.route("/criar-ticket", methods=["GET", "POST"])
@login_required
def criar_ticket():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority") or "medium"

        try:
            novo = Ticket(
                customer_id=g.user.id,
                title=title,
                description=description,
                status="open",
                priority=priority,
            )
            db.session.add(novo)
            db.session.commit()
        except ValueError as exc:
            flash(f"Erro ao criar ticket: {exc}", "danger")
            return render_template("tickets/criar_ticket.html"), 400

        flash("Ticket criado com sucesso.", "success")
        return redirect(url_for("tickets.lista"))

    return render_template("tickets/criar_ticket.html")


@bp.post("/<int:ticket_id>/close")
def fechar(ticket_id):
    """Fecha o ticket. Aceita tanto sessão web quanto Bearer token.

    Regras de autorização:
      - Sessão web: dono pode fechar próprio ticket; agent/admin podem fechar
        qualquer um.
      - Sem auth: retorna 401 (sem identificação).
    """
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({"error": "ticket não encontrado"}), 404

    user = _identifica_usuario_da_requisicao()
    if user is None:
        return jsonify({"error": "autenticação requerida"}), 401

    if not _pode_alterar_ticket(user, ticket):
        return jsonify({"error": "acesso negado"}), 403

    ticket.status = "closed"
    db.session.commit()

    if request.is_json or request.headers.get("Authorization", "").startswith("Bearer "):
        return jsonify({"id": ticket.id, "status": ticket.status}), 200
    return redirect(url_for("tickets.detalhe", ticket_id=ticket.id))


@bp.post("/<int:ticket_id>/reopen")
def reabrir(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({"error": "ticket não encontrado"}), 404

    user = _identifica_usuario_da_requisicao()
    if user is None:
        return jsonify({"error": "autenticação requerida"}), 401

    if not _pode_alterar_ticket(user, ticket):
        return jsonify({"error": "acesso negado"}), 403

    ticket.status = "open"
    db.session.commit()

    if request.is_json or request.headers.get("Authorization", "").startswith("Bearer "):
        return jsonify({"id": ticket.id, "status": ticket.status}), 200
    return redirect(url_for("tickets.detalhe", ticket_id=ticket.id))


# -------- helpers de auth dual (sessão OU bearer) --------

def _identifica_usuario_da_requisicao() -> User | None:
    """Resolve o usuário corrente, aceitando sessão OU Bearer JWT."""
    # 1) sessão web
    if getattr(g, "user", None) is not None:
        return g.user

    # 2) JWT
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            from ...auth_jwt import decodificar_token

            payload = decodificar_token(token)
            return User.query.get(int(payload["sub"]))
        except Exception:  # noqa: BLE001
            return None

    return None


def _pode_alterar_ticket(user: User, ticket: Ticket) -> bool:
    if user.role in ("agent", "admin"):
        return True
    return ticket.customer_id == user.id
