from contextlib import asynccontextmanager
import time
from http import HTTPStatus
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Response
import logging

from fastapi.params import Depends, Path, Query
from sqlalchemy.orm import Session

from apps.api.common.enum import JobStatus
from apps.api.health import get_health_status
from apps.api.pg.init import get_db, init_db
from apps.api.pg.model import JobTable
from apps.api.pg.utils import insert_if_not_exists
from apps.api.rabbitMq.init import init_rabbitmq
from apps.api.rabbitMq.message import publish_job_to_rabbitmq
from apps.api.redis.init import init_redis
from apps.api.schemas.jobRequest import JobResponse
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

@app.get("/", status_code=HTTPStatus.OK)
async def is_alive():
    logging.info("Health check...")
    return {"message": "Api service is alive"}

@app.post("/jobs")
async def create_job(raw_input: dict, response: Response, db: Session = Depends(get_db)):
    validated_input = validate_raw_input(raw_input)
    logging.info("Creating job...")

    job_dict = validated_input.model_dump()
    job_data, is_new_job = await insert_if_not_exists(db, JobTable, job_dict, idempotency_key=job_dict["idempotency_key"])

    if not is_new_job:
        response.status_code = HTTPStatus.OK
        return {"message": "Job already exists", "data": job_data}

    await publish_job_to_rabbitmq(app, job_dict, job_dict.get("priority", 1))
    response.status_code = HTTPStatus.CREATED
    return {"message": "Job created"}

@app.get("/jobs/{idempotency_key}", status_code=HTTPStatus.OK, response_model=JobResponse)
def get_job_by_id(response: Response, idempotency_key: str = Path(..., description="Idempotency key of the job to retrieve"), 
                  db: Session = Depends(get_db)):
    job = db.query(JobTable).filter_by(idempotency_key=idempotency_key).first()
    if not job:
        response.status_code = HTTPStatus.NOT_FOUND
        return {"message": f"Job with idempotency_key {idempotency_key} not found"}
        
    return job

@app.post("/jobs/{idempotency_key}/cancel")
def cancel_job(response: Response,
               idempotency_key: str = Path(..., description="Idempotency key of the job to cancel"),
               db: Session = Depends(get_db)):
    job = db.query(JobTable).filter_by(idempotency_key=idempotency_key).first()
    if not job:
        response.status_code = HTTPStatus.NOT_FOUND
        return {"message": f"Job with idempotency_key {idempotency_key} not found"}
    
    if job.status in [JobStatus.PENDING.value, JobStatus.SCHEDULED.value]:
        job.status = JobStatus.CANCELED.value
        db.commit()
        response.status_code = HTTPStatus.OK
        return {"message": "Job canceled successfully"}
    
    response.status_code = HTTPStatus.BAD_REQUEST
    return {"message": "Job cannot be canceled"}

@app.get("/jobs", status_code=HTTPStatus.OK, response_model=List[JobResponse])
def list_jobs(
    response: Response,
    status: Optional[JobStatus] = Query(None, description="Filter by job status"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    limit: int = Query(10, ge=1, le=100, description="Number of jobs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    query = db.query(JobTable)

    if status:
        query = query.filter(JobTable.status == status.value)
    if job_type:
        query = query.filter(JobTable.job_type == job_type)
        
    jobs = query.order_by(JobTable.created_at.desc()).offset(offset).limit(limit).all()

    if not jobs:
        response.status_code = HTTPStatus.NO_CONTENT
        return []
    
    return jobs

@app.get("/health", status_code=HTTPStatus.OK, response_model=dict[str, Any])
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