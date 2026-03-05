from flask import Flask, render_template
from .config import Config
from .extensions import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # cria o engine global em extensions.py
    init_db(app)

    # blueprints
    from .blueprints.pages import bp as pages_bp
    from .blueprints.tickets import bp as tickets_bp
    from .blueprints.users import bp as users_bp

    app.register_blueprint(pages_bp)                 # /
    app.register_blueprint(tickets_bp, url_prefix="/tickets")
    app.register_blueprint(users_bp, url_prefix="/users")

    # errors (sem criar arquivo errors.py, porque não existe na sua estrutura)
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    return app