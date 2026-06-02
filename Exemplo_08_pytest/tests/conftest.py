"""Fixtures compartilhadas pelos testes.

Disponíveis:
  app                  -> Flask app configurado para teste (SQLite em memória)
  client               -> cliente HTTP de teste do Flask
  usuario_cadastrado   -> User com senha "senha123" persistido no banco
  agent_cadastrado     -> User com role=agent
  customer_e_tickets   -> User customer + 3 tickets abertos
  token_de             -> factory: token_de(email) -> str (JWT pronto pra uso)
"""

from __future__ import annotations

import pytest

from microtask import create_app
from microtask.auth_jwt import gerar_token
from microtask.extensions import db
from microtask.models import Ticket, User


@pytest.fixture
def app():
    """Cria uma app Flask configurada para testes."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key-precisa-ter-32-bytes-no-minimo",
            "JWT_EXPIRES_MINUTES": 60,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente HTTP simulado para bater nas rotas."""
    return app.test_client()


@pytest.fixture
def usuario_cadastrado(app):
    """User customer com senha 'senha123'."""
    with app.app_context():
        user = User(
            name="Login Test",
            email="login@test.com",
            role="customer",
        )
        user.set_password("senha123")
        db.session.add(user)
        db.session.commit()
        # Retorna apenas o id; o objeto desanexa ao sair do context
        db.session.refresh(user)
        return {"id": user.id, "email": user.email, "password": "senha123"}


@pytest.fixture
def agent_cadastrado(app):
    """User agent com senha 'senha-agent'."""
    with app.app_context():
        user = User(name="Agente Suporte", email="agent@test.com", role="agent")
        user.set_password("senha-agent")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return {"id": user.id, "email": user.email, "password": "senha-agent"}


@pytest.fixture
def customer_e_tickets(app):
    """1 customer + 3 tickets abertos."""
    with app.app_context():
        user = User(name="Cliente Teste", email="cli@test.com", role="customer")
        user.set_password("senha-cli")
        db.session.add(user)
        db.session.commit()

        for i in range(3):
            t = Ticket(
                title=f"Ticket {i}",
                status="open",
                priority="medium",
                customer_id=user.id,
            )
            db.session.add(t)
        db.session.commit()
        db.session.refresh(user)
        return {"user_id": user.id, "email": user.email, "password": "senha-cli"}


@pytest.fixture
def token_de(app):
    """Factory: token_de('email@x.com') -> JWT string para esse usuário."""

    def _factory(email: str) -> str:
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            assert user is not None, f"usuário {email} não existe"
            return gerar_token(user)

    return _factory


@pytest.fixture
def auth_header(token_de):
    """Factory: auth_header('email@x.com') -> {'Authorization': 'Bearer <jwt>'}."""

    def _factory(email: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token_de(email)}"}

    return _factory
