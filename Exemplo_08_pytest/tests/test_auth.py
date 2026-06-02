"""Testes de autenticação, autorização e segurança."""

import pytest

from microtask.extensions import db
from microtask.models import Ticket, User


# ---------- Hash de senha ----------

@pytest.mark.auth
@pytest.mark.security
def test_senha_nao_eh_armazenada_em_texto_puro(app):
    """Senha NUNCA pode aparecer em texto puro no banco."""
    senha = "segredo-do-joao-123"
    with app.app_context():
        u = User(name="Joao", email="joao@test.com", role="customer")
        u.set_password(senha)
        db.session.add(u)
        db.session.commit()

        recuperado = User.query.filter_by(email="joao@test.com").first()
        assert recuperado.password_hash != senha
        # hashes do werkzeug começam com algo como "pbkdf2:" ou "scrypt:"
        assert ":" in recuperado.password_hash
        assert len(recuperado.password_hash) > 20


@pytest.mark.auth
def test_check_password_aceita_correta_rejeita_errada(app):
    with app.app_context():
        u = User(name="X", email="x@y.com", role="customer")
        u.set_password("certa")
        db.session.add(u)
        db.session.commit()

        assert u.check_password("certa") is True
        assert u.check_password("errada") is False
        assert u.check_password("") is False


# ---------- Login JWT ----------

@pytest.mark.auth
def test_login_com_credenciais_corretas_retorna_token(client, usuario_cadastrado):
    response = client.post(
        "/auth/login",
        json={
            "email": usuario_cadastrado["email"],
            "password": usuario_cadastrado["password"],
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert len(data["access_token"]) > 20
    # JWT tem 3 segmentos separados por ponto
    assert data["access_token"].count(".") == 2


@pytest.mark.auth
def test_login_com_senha_errada_retorna_401(client, usuario_cadastrado):
    response = client.post(
        "/auth/login",
        json={"email": usuario_cadastrado["email"], "password": "errada"},
    )
    assert response.status_code == 401


@pytest.mark.auth
def test_login_com_usuario_inexistente_retorna_401(client):
    """NÃO retornar 404 — entrega informação para enumeração."""
    response = client.post(
        "/auth/login",
        json={"email": "naoexiste@test.com", "password": "qualquer"},
    )
    assert response.status_code == 401


@pytest.mark.auth
@pytest.mark.security
def test_login_nao_revela_se_usuario_existe(client, usuario_cadastrado):
    """A resposta para usuário inexistente e senha errada deve ser a MESMA."""
    r1 = client.post(
        "/auth/login",
        json={"email": usuario_cadastrado["email"], "password": "errada"},
    )
    r2 = client.post(
        "/auth/login",
        json={"email": "naoexiste@test.com", "password": "qualquer"},
    )
    assert r1.status_code == r2.status_code == 401
    assert r1.get_json() == r2.get_json()


# ---------- Rotas protegidas por token ----------

@pytest.mark.auth
def test_rota_protegida_sem_token_retorna_401(client):
    response = client.get("/api/tickets")
    assert response.status_code == 401


@pytest.mark.auth
def test_token_invalido_retorna_401(client):
    response = client.get(
        "/api/tickets",
        headers={"Authorization": "Bearer token-fake-123"},
    )
    assert response.status_code == 401


@pytest.mark.auth
def test_token_mal_formado_retorna_401(client):
    """Sem 'Bearer ', também 401."""
    response = client.get(
        "/api/tickets", headers={"Authorization": "naoBearer xyz"}
    )
    assert response.status_code == 401


@pytest.mark.auth
def test_rota_protegida_com_token_valido_funciona(client, usuario_cadastrado, auth_header):
    headers = auth_header(usuario_cadastrado["email"])
    response = client.get("/api/tickets", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


@pytest.mark.auth
def test_endpoint_me_retorna_dados_do_usuario_do_token(client, usuario_cadastrado, auth_header):
    headers = auth_header(usuario_cadastrado["email"])
    response = client.get("/api/me", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == usuario_cadastrado["email"]
    assert data["role"] == "customer"


# ---------- Mass assignment ----------

@pytest.mark.auth
@pytest.mark.security
def test_usuario_nao_consegue_se_autopromover_a_admin(client, app):
    """O atacante manda role=admin e is_admin=true; defesa ignora os dois."""
    payload = {
        "name": "Hacker",
        "email": "hack@test.com",
        "password": "abc1234",
        "role": "admin",  # <- tentativa
        "is_admin": True,  # <- tentativa
        "created_at": "1970-01-01T00:00:00",
    }
    response = client.post("/users/registrar", json=payload)
    assert response.status_code == 201

    with app.app_context():
        u = User.query.filter_by(email="hack@test.com").first()
        assert u is not None
        # Não importa o que o cliente mandou — role tem que ser o default seguro
        assert u.role == "customer"
        assert u.role != "admin"


@pytest.mark.auth
@pytest.mark.security
def test_registrar_ignora_id_enviado_pelo_cliente(client, app):
    """Cliente tenta forçar id=9999; o banco decide o id."""
    payload = {
        "name": "Tenta Id",
        "email": "tenta@x.com",
        "password": "abc1234",
        "id": 9999,
    }
    response = client.post("/users/registrar", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] != 9999

    with app.app_context():
        u = User.query.filter_by(email="tenta@x.com").first()
        assert u.id != 9999


# ---------- Autorização (broken access control) ----------

@pytest.mark.auth
@pytest.mark.security
def test_usuario_nao_consegue_fechar_ticket_de_outro(client, app, auth_header):
    # Ana e Beto, customers; ticket é da Ana.
    with app.app_context():
        ana = User(name="Ana", email="ana@x.com", role="customer")
        ana.set_password("123456")
        beto = User(name="Beto", email="beto@x.com", role="customer")
        beto.set_password("456789")
        db.session.add_all([ana, beto])
        db.session.commit()

        ticket = Ticket(
            title="Da Ana",
            customer_id=ana.id,
            status="open",
            priority="medium",
        )
        db.session.add(ticket)
        db.session.commit()
        ticket_id = ticket.id

    # Beto loga e tenta fechar o ticket da Ana
    headers = auth_header("beto@x.com")
    response = client.post(f"/tickets/{ticket_id}/close", headers=headers)
    assert response.status_code == 403

    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        assert ticket.status == "open"


@pytest.mark.auth
def test_agent_pode_fechar_ticket_de_outro(client, app, auth_header):
    with app.app_context():
        ana = User(name="Ana", email="ana@x.com", role="customer")
        ana.set_password("123456")
        agente = User(name="Agente", email="agente@x.com", role="agent")
        agente.set_password("abcdef")
        db.session.add_all([ana, agente])
        db.session.commit()

        ticket = Ticket(
            title="Da Ana", customer_id=ana.id, status="open", priority="medium"
        )
        db.session.add(ticket)
        db.session.commit()
        ticket_id = ticket.id

    headers = auth_header("agente@x.com")
    response = client.post(f"/tickets/{ticket_id}/close", headers=headers)
    assert response.status_code == 200

    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        assert ticket.status == "closed"


@pytest.mark.auth
@pytest.mark.security
def test_customer_nao_acessa_lista_de_usuarios_api(client, usuario_cadastrado, auth_header):
    headers = auth_header(usuario_cadastrado["email"])
    response = client.get("/api/users", headers=headers)
    assert response.status_code == 403


@pytest.mark.auth
def test_agent_acessa_lista_de_usuarios_api(client, agent_cadastrado, auth_header):
    headers = auth_header(agent_cadastrado["email"])
    response = client.get("/api/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


# ---------- Token expirado ----------

@pytest.mark.auth
@pytest.mark.security
def test_token_expirado_retorna_401(client, app, usuario_cadastrado):
    """Forja token com exp no passado e verifica que API rejeita."""
    import jwt
    from datetime import datetime, timedelta, timezone

    with app.app_context():
        passado = datetime.now(timezone.utc) - timedelta(hours=1)
        token = jwt.encode(
            {"sub": str(usuario_cadastrado["id"]), "role": "customer", "exp": passado},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    response = client.get(
        "/api/tickets", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
