

from http import HTTPStatus
import logging

from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from apps.api.pg.init import get_db
from apps.api.pg.model import JobTable
from apps.api.redis.init import get_redis_client
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def insert_if_not_exists(db, table, data, idempotency_key):
    try:
        redis = get_redis_client()
        redis_key = await redis.get(f"{table.__tablename__}:{idempotency_key}")
        if redis_key:
            logger.warning(f"Data with idempotency_key {idempotency_key} already exists in Redis cache")
            #posgress db will return the record with the existing idempotency_key, so we can skip the insert operation and return the existing record
            exist_record = db.query(table).filter_by(idempotency_key=idempotency_key).first()
            
            return exist_record, False
        
        upsert = insert(table).values(**data)
        upsert = upsert.on_conflict_do_update(index_elements=["idempotency_key"], set_=data)
        db.execute(upsert)
        db.commit()

        await redis.set(f"{table.__tablename__}:{idempotency_key}", idempotency_key, ex=24*60*60)
        logger.info(f"Data with idempotency_key {idempotency_key} inserted into Redis and Postgres database")

        return data, True
    
    except Exception as e:
        #reset failed transaction
        db.rollback()
        logger.error(f"Failed to insert data: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error occurred") 

def update_table(db: Session,table: JobTable, updated_value: dict, idempotency_key: str):
    try:
        db.query(table).filter_by(idempotency_key=idempotency_key).update(updated_value)
        db.commit()
        logger.info(f"Data with idempotency_key {idempotency_key} updated in Postgres database")
    except Exception as e:
        logger.error(f"Failed to update data: {e}")
        db.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error occurred")
