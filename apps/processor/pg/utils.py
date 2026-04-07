

from http import HTTPStatus
import logging

from fastapi import HTTPException
from apps.processor.pg.init import get_db
from apps.processor.pg.model import JobTable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_table(table_name: JobTable, updated_value: dict, idempotency_key: str):
    with get_db() as db:
        try:
            db.query(table_name).filter_by(idempotency_key=idempotency_key).update(updated_value)
            db.commit()
            logger.info(f"Data with idempotency_key {idempotency_key} updated in Postgres database")
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            db.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error occurred")

def is_job_canceled(idempotency_key: str) -> bool:
    with get_db() as db:
        job = db.query(JobTable).filter_by(idempotency_key=idempotency_key).first()
        if job and job.status == "canceled":
            logger.info(f"Job with idempotency_key {idempotency_key} is canceled. Skipping processing.")
            return True
    return False