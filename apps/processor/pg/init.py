

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from apps.processor.common.constants import get_config
from apps.processor.pg.model import Base
from contextlib import contextmanager

def init_db():
    global SessionLocal
    config = get_config()
    DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    return engine


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
