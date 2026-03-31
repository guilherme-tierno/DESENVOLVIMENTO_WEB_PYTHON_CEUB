from dotenv import load_dotenv
import os 

load_dotenv()

class Config:
    # O Flask-SQLAlchemy procura automaticamente o SQLACHEMY_DATABASE_URI para se conectar ao banco de dados.
    SQLALCHEMY_DATABASE_URI = os.getenv("MINHAS_CREDENCIAIS")

    # não essenciais neste momento, mas importantes para segurança e performance
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False