from sqlalchemy import create_engine

engine = None

def init_db(app):
    global engine
    db_url = app.config["DATABASE_URL"]
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        future=True
    )