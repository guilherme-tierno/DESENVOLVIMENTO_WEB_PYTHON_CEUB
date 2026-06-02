"""Configuração lida do ambiente (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///helpdesk_dev.db",  # fallback para quem não tem MySQL local
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tempo de expiração do token JWT, em minutos
    JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
