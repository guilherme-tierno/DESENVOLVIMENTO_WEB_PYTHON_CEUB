from flask import render_template, abort
from . import bp
from ...models import list_tickets, get_ticket

@bp.get("/")
def lista():
    tickets = list_tickets(limit=50)
    return render_template("tickets/lista.html", tickets=tickets)

@bp.get("/<int:ticket_id>")
def detalhe(ticket_id):
    data = get_ticket(ticket_id)
    if not data:
        abort(404)
    return render_template(
        "tickets/detalhe.html",
        ticket=data["ticket"],
        updates=data["updates"]
    )