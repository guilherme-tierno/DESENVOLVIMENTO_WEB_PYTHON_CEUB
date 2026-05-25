from flask import abort, flash, g, redirect, render_template, request, url_for

from . import bp
from ...extensions import db
from ...models import Ticket, TicketUpdate
from ..auth.routes import login_required


@bp.get("/")
@login_required
def lista():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template("tickets/lista.html", tickets=tickets)


@bp.get("/<int:ticket_id>")
@login_required
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
        priority = request.form.get("priority")

        novo_ticket = Ticket(
            customer_id=g.user.id,
            title=title,
            description=description,
            status="open",
            priority=priority,
        )

        db.session.add(novo_ticket)
        db.session.commit()

        flash("Ticket criado com sucesso.", "success")
        return redirect(url_for("tickets.lista"))

    return render_template("tickets/criar_ticket.html")


@bp.get("/add-update")
@login_required
def add_update():
    ticket = Ticket.query.get(1)
    user = g.user

    if not ticket or not user:
        abort(404)

    update = TicketUpdate(
        ticket_id=ticket.id,
        author_id=user.id,
        message="Atualização automática de teste.",
    )

    db.session.add(update)
    db.session.commit()

    return f"Update criado com sucesso para o ticket {ticket.id}"
