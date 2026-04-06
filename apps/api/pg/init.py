

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from apps.api.common.constants import getConfig

SessionLocal = None

def init_db():
    config = getConfig()
    DATABASE_URL = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
