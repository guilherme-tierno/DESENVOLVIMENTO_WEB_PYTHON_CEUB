import pytest
from microtask import create_app
from microtask.extensions import db

@pytest.fixture
def app():
    # Configurações de teste, forçando o SQLite em memória
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False  # Desabilita CSRF se usar formulários nos testes
    })

    # Cria o contexto da aplicação para o SQLAlchemy trabalhar
    with app.app_context():
        db.create_all()  # Cria as tabelas baseadas nos seus models
        
        yield app        # O teste roda aqui
        
        db.session.remove()
        db.drop_all()    # Limpa o banco após o fim do teste

@pytest.fixture
def client(app):
    """Um cliente de testes que permite fazer requisições HTTP."""
    return app.test_client()