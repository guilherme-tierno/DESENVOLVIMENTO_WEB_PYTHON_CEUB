"""Testes do CRUD de User."""

import pytest

from microtask.extensions import db
from microtask.models import User


# ---------- CREATE ----------

@pytest.mark.crud
def test_criar_usuario_com_dados_validos(client):
    payload = {
        "name": "Ana Costa",
        "email": "ana@campus.edu.br",
        "role": "customer",
        "password": "minha-senha",
    }
    response = client.post("/users/criar-usuario", data=payload, follow_redirects=True)
    assert response.status_code == 200
    assert b"Ana Costa" in response.data


@pytest.mark.crud
def test_criar_usuario_persiste_no_banco(client, app):
    payload = {
        "name": "Ana Costa",
        "email": "ana@campus.edu.br",
        "role": "customer",
        "password": "senha-forte",
    }
    client.post("/users/criar-usuario", data=payload)

    with app.app_context():
        user = User.query.filter_by(email="ana@campus.edu.br").first()
        assert user is not None
        assert user.name == "Ana Costa"
        assert user.role == "customer"


@pytest.mark.crud
def test_criar_usuario_email_duplicado_retorna_erro(client):
    payload = {
        "name": "Primeiro",
        "email": "duplicado@x.com",
        "role": "customer",
        "password": "abc1234",
    }
    primeiro = client.post("/users/criar-usuario", data=payload)
    assert primeiro.status_code in (200, 201)

    segundo = client.post("/users/criar-usuario", data=payload)
    assert segundo.status_code in (400, 409)
    # mensagem em português OU expressão típica de banco
    body = segundo.data.lower()
    assert (
        b"j\xc3\xa1 existe" in body
        or b"duplicate" in body
        or b"cadastrado" in body
    )


# ---------- Validação com parametrize ----------

@pytest.mark.crud
@pytest.mark.parametrize(
    "email_invalido",
    [
        "",
        "semarroba.com",
        "@semnome.com",
        "a@",
        "   ",
        "sem-arroba",
    ],
)
def test_criar_usuario_rejeita_email_invalido(client, email_invalido):
    payload = {
        "name": "X",
        "email": email_invalido,
        "role": "customer",
        "password": "abc1234",
    }
    response = client.post("/users/criar-usuario", data=payload)
    assert response.status_code == 400


@pytest.mark.crud
@pytest.mark.parametrize("role_invalido", ["root", "superadmin", "", "guest"])
def test_criar_usuario_rejeita_role_invalida(client, role_invalido):
    payload = {
        "name": "Ana",
        "email": "ana@x.com",
        "role": role_invalido,
        "password": "abc1234",
    }
    response = client.post("/users/criar-usuario", data=payload)
    assert response.status_code == 400


# ---------- READ ----------

@pytest.mark.crud
def test_listar_usuarios_retorna_todos(client, app):
    """Cria 3 usuários e verifica que todos aparecem na listagem."""
    # Login fictício direto via session para passar pelo login_required:
    with client.session_transaction() as sess:
        # Cria um admin para autenticar e ver a listagem
        with app.app_context():
            admin = User(name="Admin", email="admin@x.com", role="admin")
            admin.set_password("xxxxxx")
            db.session.add(admin)
            db.session.commit()
            sess["user_id"] = admin.id

    nomes = ["Carlos Silva", "Diana Lima", "Eduardo Costa"]
    for i, n in enumerate(nomes):
        client.post(
            "/users/criar-usuario",
            data={
                "name": n,
                "email": f"u{i}@x.com",
                "role": "customer",
                "password": "abc1234",
            },
        )

    response = client.get("/users/")
    assert response.status_code == 200
    for nome in nomes:
        assert nome.encode() in response.data


# ---------- DELETE ----------

@pytest.mark.crud
def test_excluir_usuario_remove_do_banco(client, app):
    with app.app_context():
        user = User(name="Temporário", email="temp@test.com", role="customer")
        user.set_password("abc1234")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    response = client.post(f"/users/{user_id}/excluir")
    assert response.status_code == 200

    with app.app_context():
        assert User.query.get(user_id) is None


@pytest.mark.crud
def test_excluir_usuario_inexistente_retorna_404(client):
    response = client.post("/users/99999/excluir")
    assert response.status_code == 404
