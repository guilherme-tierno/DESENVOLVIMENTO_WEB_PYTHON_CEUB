from flask import Flask, render_template
from .config import Config
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # inicializa ORM e migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # blueprints
    from .blueprints.pages import bp as pages_bp
    from .blueprints.tickets import bp as tickets_bp
    from .blueprints.users import bp as users_bp

    app.register_blueprint(pages_bp)                 # /
    app.register_blueprint(tickets_bp, url_prefix="/tickets")
    app.register_blueprint(users_bp, url_prefix="/users")

    # erro 404
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    return app