"""Endpoints JSON protegidos por JWT.

Listagem de tickets disponível apenas para usuário autenticado via token.
"""

from flask import g, jsonify

from ...auth_jwt import role_required, token_required
from ...models import Ticket, User
from . import bp


@bp.get("/tickets")
@token_required
def listar_tickets_api():
    """Retorna lista de tickets do usuário atual.

    - customer: vê apenas os próprios.
    - agent/admin: vê todos.
    """
    user = g.current_user
    if user.role in ("agent", "admin"):
        tickets = (
            Ticket.query.order_by(Ticket.created_at.desc(), Ticket.id.desc()).all()
        )
    else:
        tickets = (
            Ticket.query.filter_by(customer_id=user.id)
            .order_by(Ticket.created_at.desc(), Ticket.id.desc())
            .all()
        )

    return jsonify(
        [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "customer_id": t.customer_id,
            }
            for t in tickets
        ]
    ), 200


@bp.get("/me")
@token_required
def me():
    """Retorna dados do usuário do token."""
    u = g.current_user
    return jsonify(
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
    ), 200


@bp.get("/users")
@token_required
@role_required("agent", "admin")
def listar_users_api():
    """Lista todos os usuários — só para agent/admin."""
    users = User.query.order_by(User.name.asc()).all()
    return jsonify(
        [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]
    ), 200
