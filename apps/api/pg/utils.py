

from http import HTTPStatus
import logging

from fastapi import HTTPException
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
logging.getLogger(__name__)

def insert_if_not_exists(db, table, data, unique_fields):
    #TODO: change it to check with Redis cache first (24h ttl) before inserting into the database - instead of this solution
    try:
        insert_command = insert(table).values(**data).on_conflict_do_nothing(index_elements=unique_fields)
        db.execute(insert_command)
        db.commit()

    except SQLAlchemyError as e:
        #reset failed transaction
        db.rollback()
        logging.error(f"Failed to insert data: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error occurred") 