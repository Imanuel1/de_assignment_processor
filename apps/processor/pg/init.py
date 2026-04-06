

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from apps.api.common.constants import get_config
from apps.api.pg.model import Base

SessionLocal: Session = None

def init_db():
    global SessionLocal
    config = get_config()
    DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
