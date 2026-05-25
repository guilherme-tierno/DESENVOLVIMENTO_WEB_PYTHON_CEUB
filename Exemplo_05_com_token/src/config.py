import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-inseguro")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-inseguro")
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
