from contextlib import asynccontextmanager
from http import HTTPStatus
import logging
import time

from fastapi import FastAPI
from apps.processor.pg.init import init_db
from apps.processor.rabbitMq.init import init_rabbitmq

logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")
    init_db()
    await init_rabbitmq()
    yield
    logging.info("Shutting down...")

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    logging.info("Health check...")
    return {"message": "Service is alive", "status": HTTPStatus.OK}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)