from flask import render_template, request, redirect, url_for, abort
from . import bp
from ...models import Ticket, User, TicketUpdate # Importado no topo
from ...extensions import db

@bp.get("/")
def lista():
    tickets = Ticket.query.all()
    return render_template("tickets/lista.html", tickets=tickets)

@bp.get("/<int:ticket_id>")
def detalhe(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        abort(404)
    return render_template("tickets/detalhe.html", ticket=ticket)

@bp.route("/criar-ticket", methods=["GET", "POST"])
def criar_ticket():
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")

        usuario = User.query.get(customer_id)
        if not usuario:
            return "Usuário não encontrado", 404

        novo_ticket = Ticket(
            customer_id=usuario.id,
            title=title,
            description=description,
            status="open",
            priority=priority
        )

        db.session.add(novo_ticket)
        db.session.commit()
        return redirect(url_for("tickets.lista"))

    usuarios = User.query.all()
    return render_template("tickets/criar_ticket.html", usuarios=usuarios)

@bp.get("/resolver-teste")
def resolver_teste():
    ticket = Ticket.query.get(2)
    if not ticket:
        return "Erro: Ticket de ID 2 não encontrado.", 404
    
    ticket.status = "resolved"
    db.session.commit()
    return f"Sucesso! O Ticket #{ticket.id} agora está como {ticket.status}."