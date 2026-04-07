from contextlib import asynccontextmanager
import time
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
import logging

from fastapi.params import Depends
from sqlalchemy.orm import Session

from apps.api.common.enum import JobStatus
from apps.api.health import get_health_status
from apps.api.pg.init import get_db, init_db
from apps.api.pg.model import JobTable
from apps.api.pg.utils import insert_if_not_exists
from apps.api.rabbitMq.init import init_rabbitmq
from apps.api.rabbitMq.message import publish_job_to_rabbitmq
from apps.api.redis.init import init_redis
from apps.api.utils.validate import validate_raw_input
logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")
    init_db(app)
    init_redis()
    await init_rabbitmq(app)
    yield
    logging.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def is_alive():
    logging.info("Health check...")
    return {"message": "Api service is alive", "status": HTTPStatus.OK}

@app.post("/jobs")
async def create_job(raw_input: dict, db: Session = Depends(get_db)):
    validated_input = validate_raw_input(raw_input)
    logging.info("Creating job...")

    job_dict = validated_input.model_dump()
    job_data, is_new_job = await insert_if_not_exists(db, JobTable, job_dict, idempotency_key=job_dict["idempotency_key"])

    if not is_new_job:
        return {"message": "Job already exists", "status_code": HTTPStatus.OK, "data": job_data}

    await publish_job_to_rabbitmq(app, job_dict, job_dict.get("priority", 1))

    return {"message": "Job created", "status_code": HTTPStatus.CREATED}


@app.post("/job/{idempotency_key}/cancel")
def cancel_job(idempotency_key: str, db: Session = Depends(get_db)):
    job = db.query(JobTable).filter_by(idempotency_key=idempotency_key).first()
    if not job:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job not found")
    
    if job.status in [JobStatus.PENDING, JobStatus.SCHEDULED]:
        job.status = JobStatus.CANCELED
        db.commit()
        return {"message": "Job canceled successfully", "status_code": HTTPStatus.OK}
    
    return {"message": "Job cannot be canceled", "status_code": HTTPStatus.BAD_REQUEST}


@app.get("/health")
async def services_health_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "postgres": "up",
        "rabbitmq": "up",
        "redis": "up",
        "queue_stats": {}
    }

    await get_health_status(db, health_status)

    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)