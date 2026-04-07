import logging

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text

from apps.api.common.constants import get_config
from apps.api.redis.init import get_redis_client
logging.basicConfig(level=logging.INFO)


async def get_health_status(db: Session, health_status: dict):
    check_postgres_health(db, health_status)
    await check_rabbitmq_health(health_status)
    await check_redis_health(health_status)


def check_postgres_health(db: Session, health_status: dict):
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logging.warning(f"Postgres health check failed: {e}")
        health_status["postgres"] = "down"
        health_status["status"] = "unhealthy"

async def check_rabbitmq_health(health_status: dict):
    config = get_config()
    RABBITMQ_MANAGER_URL = f"http://{config.RABBITMQ_HOST}:15672/api/queues/%2f/jobs"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(RABBITMQ_MANAGER_URL, auth=(config.RABBITMQ_USER, config.RABBITMQ_PASS))
            if response.status_code == 200:
                data = response.json()
                health_status["queue_stats"] = {
                    "message_count": data.get("messages", 0),
                    "messages_unacknowledged": data.get("messages_unacknowledged", 0),
                    "consumer_count": data.get("consumers", 0),
                    "state": data.get("state", "unknown")
                }
            else:
                health_status["rabbitmq"] = f"error_{response.status_code}"
        except Exception as e:
            logging.warning(f"RabbitMQ health check failed: {e}")
            health_status["rabbitmq"] = "down"
            health_status["status"] = "unhealthy"

async def check_redis_health(health_status: dict):
    redis_client = get_redis_client()
    try:
        await redis_client.ping()
        health_status["redis"] = "up"
    except Exception as e:
        logging.warning(f"Redis health check failed: {e}")
        health_status["redis"] = "down"