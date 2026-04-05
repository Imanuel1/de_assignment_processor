from contextlib import asynccontextmanager

from fastapi import FastAPI
import logging

logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")
    yield
    logging.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def is_alive():
    logging.info("Health check...")
    return {"message": "Service is alive"}

@app.post("/jobs")
async def create_job():
    logging.info("Creating job...")
    return {"message": "Job created"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)