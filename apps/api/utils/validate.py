
from http import HTTPStatus
import logging

from fastapi import HTTPException
from pydantic import ValidationError

from apps.api.schemas.jobRequest import JobRequest
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_raw_input(raw_input: dict):
    try:
        validate_input = JobRequest.model_validate(raw_input)
    except ValidationError as e:
        error_string = {".".join(map(str, error['loc'])): error['msg'] for error in e.errors()}
        logger.error(f"Failed schema validation: {error_string}")

        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid input format")
    
    #TODO: if needed, do a tranformation to the input data

    return validate_input