import logging
from fastapi import FastAPI

import aio_pika
from apps.api.common.constants import get_config
logger = logging.getLogger(__name__)


async def init_rabbitmq(app: FastAPI):
    try:
        config = get_config()
        app.state.connection = await aio_pika.connect_robust(f"amqp://{config.RABBITMQ_USER}:{config.RABBITMQ_PASS}@{config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}/")
        app.state.channel = await app.state.connection.channel()

        await app.state.channel.declare_queue("jobs", arguments={"x-max-priority": config.RABBITMQ_QUEUE_PRIORITY}, durable=True)
        logger.info("RabbitMQ connection established and queue declared.")
    except Exception as e:
        logger.error(f"Failed to initialize RabbitMQ: {e}")