

from fastapi import FastAPI, Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from apps.api.common.constants import get_config
from apps.api.pg.model import Base

def init_db(app: FastAPI) -> Engine:
    config = get_config()
    DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    app.state.db_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    return engine

def get_db(request: Request):
    db = request.app.state.db_session_factory()
    try:
        yield db
    finally:
        db.close()
