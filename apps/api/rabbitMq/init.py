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
        await app.state.channel.set_qos(prefetch_count=1)

        delayed_exchange = await app.state.channel.declare_exchange("delayed_jobs_exchange", type="x-delayed-message", passive=True, durable=True,
            # This tells it how to route once the delay is over
            arguments={ "x-delayed-type": "direct" }
        )

        queue =await app.state.channel.declare_queue("jobs", arguments={"x-max-priority": config.RABBITMQ_QUEUE_PRIORITY}, durable=True)
        await queue.bind(delayed_exchange, routing_key="jobs")
        app.state.delayed_exchange = delayed_exchange

        logger.info("RabbitMQ connection established and queue declared.")
    except Exception as e:
        logger.error(f"Failed to initialize RabbitMQ: {e}")