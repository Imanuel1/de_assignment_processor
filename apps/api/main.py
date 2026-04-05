from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI
import logging

from fastapi.params import Depends
from sqlalchemy.orm import Session

from apps.api.pg.init import Base, engine, init_db
from apps.api.rabbitMq.message import publish_job_to_rabbitmq
from apps.api.utils.validate import validate_raw_input

logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")
    Base.metadata.create_all(bind=engine)
    yield
    logging.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def is_alive():
    logging.info("Health check...")
    return {"message": "Service is alive", "status": "ok"}

@app.post("/jobs")
async def create_job(raw_input: dict, db: Session = Depends(init_db)):
    validated_input = validate_raw_input(raw_input)
    logging.info("Creating job...")

    #TODO: save job to db
    db.add(validated_input)
    db.commit()
    db.refresh(validated_input)

    #TODO: publish job to RabbitMQ
    await publish_job_to_rabbitmq(app, validated_input, priority=1)

    return {"message": "Job created", "status_code": HTTPStatus.CREATED}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)