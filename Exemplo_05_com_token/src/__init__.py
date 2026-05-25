from flask import Flask
from flask_jwt_extended import JWTManager
from src.config import config_by_name
from src.blueprints.auth import auth_bp


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[env])

    JWTManager(app)

    app.register_blueprint(auth_bp)

    return app
