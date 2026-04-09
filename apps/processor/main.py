import asyncio
from contextlib import asynccontextmanager
from http import HTTPStatus
import logging
import time

from fastapi import FastAPI
from apps.processor.pg.init import init_db
from apps.processor.rabbitMq.init import init_rabbitmq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

active_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    db_engine = init_db()
    rabbit_connection = await init_rabbitmq()
    #store the active_task for the consumer can use it
    app.state.active_tasks = active_tasks
    yield
    if rabbit_connection:
        logger.info("Closing RabbitMQ connection (stopping consumers)...")
        await rabbit_connection.close()
    if active_tasks:
        logger.info(f"Waiting for {len(active_tasks)} active jobs to finish...")
        # Wait until all tasks in the set are done
        await asyncio.gather(*active_tasks, return_exceptions=True)
    db_engine.dispose()
    logger.info("Shutting down...")
    

app = FastAPI(lifespan=lifespan)


@app.get("/", status_code=HTTPStatus.OK)
async def root():
    logger.info("Health check...")
    return {"message": "Service is alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)