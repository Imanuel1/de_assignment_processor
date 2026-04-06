

from http import HTTPStatus
import logging

from fastapi import HTTPException
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError

from apps.api.redis.init import get_redis_client
from apps.processor.pg.model import JobTable
logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)

async def insert_if_not_exists(db, table, data, idempotency_key):
    try:
        redis = get_redis_client()
        redis_key = await redis.get(f"{table.__tablename__}:{idempotency_key}")
        if redis_key:
            logging.warning(f"Data with idempotency_key {idempotency_key} already exists in Redis cache")
            #posgress db will return the record with the existing idempotency_key, so we can skip the insert operation and return the existing record
            exist_record = db.query(table).filter_by(idempotency_key=idempotency_key).first()
            
            return {"message": "Job already exists", "status_code": HTTPStatus.OK, "data": exist_record}
        
        db.add(table(**data))
        db.commit()

        await redis.set(f"{table.__tablename__}:{idempotency_key}", idempotency_key, ex=24*60*60)
        logging.info(f"Data with idempotency_key {idempotency_key} inserted into Redis and Postgres database")

    except Exception as e:
        #reset failed transaction
        db.rollback()
        logging.error(f"Failed to insert data: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error occurred") 