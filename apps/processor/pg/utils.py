

from http import HTTPStatus
import logging

from fastapi import HTTPException

from apps.api.pg.init import get_db
logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)

def update_table(table_name: str, updated_value: dict, idempotency_key: str):
    try:
        db = get_db()
        #TODO: implement the logic to update the table based on the table_name, and on updated value and idempotency_key, 
        # this function will be used to update the job status and other fields in the database after processing the job
        #the updated value can be: {"status": "completed", "result": {"output": "some output"}, "error": None} or {"status": "failed", "result": None, "error": "some error message"}

        db.query(table_name).filter_by(idempotency_key=idempotency_key).update(updated_value)
        db.commit()
        logging.info(f"Data with idempotency_key {idempotency_key} updated in Postgres database")
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to update data: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error occurred")