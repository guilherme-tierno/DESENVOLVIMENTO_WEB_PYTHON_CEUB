"""Testes de CRUD de Ticket."""

import pytest

from microtask.extensions import db
from microtask.models import Ticket, User


# ---------- READ ----------

@pytest.mark.crud
def test_lista_tickets_retorna_todos_criados(client, customer_e_tickets):
    response = client.get("/tickets/")
    assert response.status_code == 200
    # cada um dos 3 tickets aparece pelo nome "Ticket 0", "Ticket 1", "Ticket 2"
    assert b"Ticket 0" in response.data
    assert b"Ticket 1" in response.data
    assert b"Ticket 2" in response.data


@pytest.mark.crud
def test_listar_tickets_ordenado_por_data_desc(client, app, customer_e_tickets):
    response = client.get("/tickets/")
    assert response.status_code == 200
    body = response.data.decode()
    # O mais recente (Ticket 2) tem que aparecer ANTES do mais antigo (Ticket 0)
    assert body.index("Ticket 2") < body.index("Ticket 0")


@pytest.mark.crud
def test_detalhe_de_ticket_inexistente_retorna_404(client):
    response = client.get("/tickets/99999")
    assert response.status_code == 404


# ---------- UPDATE: close / reopen ----------

@pytest.mark.crud
def test_fechar_ticket_muda_status_para_closed(client, app, customer_e_tickets, auth_header):
    headers = auth_header(customer_e_tickets["email"])

    with app.app_context():
        ticket = Ticket.query.first()
        ticket_id = ticket.id
        assert ticket.status == "open"

    response = client.post(f"/tickets/{ticket_id}/close", headers=headers)
    assert response.status_code == 200

    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        assert ticket.status == "closed"


@pytest.mark.crud
def test_reabrir_ticket_volta_para_open(client, app, customer_e_tickets, auth_header):
    headers = auth_header(customer_e_tickets["email"])

    with app.app_context():
        ticket = Ticket.query.first()
        ticket_id = ticket.id

    # fecha
    client.post(f"/tickets/{ticket_id}/close", headers=headers)
    # reabre
    response = client.post(f"/tickets/{ticket_id}/reopen", headers=headers)
    assert response.status_code == 200

    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        assert ticket.status == "open"


@pytest.mark.crud
def test_fechar_ticket_sem_autenticacao_retorna_401(client, customer_e_tickets):
    """Sem header de Authorization, a operação é rejeitada."""
    response = client.post("/tickets/1/close")
    assert response.status_code == 401


# ---------- CREATE com relacionamento ----------

@pytest.mark.crud
def test_criar_ticket_associa_ao_customer(app):
    """Persistência direta no model com FK para User."""
    with app.app_context():
        u = User(name="Dono", email="dono@x.com", role="customer")
        u.set_password("abc1234")
        db.session.add(u)
        db.session.commit()

        t = Ticket(
            title="Meu ticket",
            description="descrição qualquer",
            customer_id=u.id,
            status="open",
            priority="medium",
        )
        db.session.add(t)
        db.session.commit()

        recuperado = Ticket.query.first()
        assert recuperado.customer_id == u.id
        assert recuperado.customer.email == "dono@x.com"


@pytest.mark.crud
def test_criar_ticket_com_customer_inexistente_falha(app):
    """FK para User inexistente deve falhar no commit."""
    from sqlalchemy.exc import IntegrityError

    with app.app_context():
        # SQLite por padrão não força FK. Ativamos para esse teste.
        db.session.execute(db.text("PRAGMA foreign_keys=ON"))

        t = Ticket(
            title="Sem dono",
            customer_id=99999,
            status="open",
            priority="medium",
        )
        db.session.add(t)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


@pytest.mark.crud
@pytest.mark.parametrize("titulo_ruim", ["", "  ", "ab"])
def test_criar_ticket_rejeita_titulo_curto(app, titulo_ruim):
    with app.app_context():
        u = User(name="X", email="x@x.com", role="customer")
        u.set_password("abc1234")
        db.session.add(u)
        db.session.commit()

        with pytest.raises(ValueError):
            Ticket(
                title=titulo_ruim,
                customer_id=u.id,
                status="open",
                priority="medium",
            )


@pytest.mark.crud
@pytest.mark.parametrize("prio_ruim", ["normal", "urgent", "", "HIGH"])
def test_criar_ticket_rejeita_prioridade_invalida(app, prio_ruim):
    with app.app_context():
        u = User(name="X", email="x@x.com", role="customer")
        u.set_password("abc1234")
        db.session.add(u)
        db.session.commit()

        with pytest.raises(ValueError):
            Ticket(
                title="Ticket OK",
                customer_id=u.id,
                status="open",
                priority=prio_ruim,
            )
