"""Factory da aplicação Flask.

`create_app(test_config=None)`:
    - Sem argumento: usa configuração de Config (lê .env, conecta MySQL).
    - Com dicionário: sobrescreve a configuração. Usado pelo pytest para
      injetar SQLite em memória e TESTING=True.
"""

from flask import Flask, render_template

from .config import Config
from .extensions import db, migrate


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Garantir que os models sejam importados antes de quem usa db.create_all()
    from . import models  # noqa: F401

    # Blueprints
    from .blueprints.pages import bp as pages_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.users import bp as users_bp
    from .blueprints.tickets import bp as tickets_bp
    from .blueprints.api import bp as api_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(tickets_bp, url_prefix="/tickets")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    return app
