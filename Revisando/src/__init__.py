from flask import Flask
from .config import Config
from .extensions import db
from .routes import register_routes
from flask_migrate import Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # inicializa o banco
    db.init_app(app)
    migrate.init_app(app, db)
    
    # registra as rotas
    register_routes(app)

    return app