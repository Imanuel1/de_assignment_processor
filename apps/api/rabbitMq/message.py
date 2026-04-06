import logging

import aio_pika
from fastapi import FastAPI

from apps.api.schemas.jobRequest import JobRequest
logger = logging.getLogger(__name__)


async def publish_job_to_rabbitmq(app: FastAPI, job_data: JobRequest, priority: int = 1):
    try:
        await app.state.channel.default_exchange.publish(
           aio_pika.Message(
                body=job_data.model_dump_json().encode(), 
                priority=priority, 
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT, 
                headers={"x-retry-count": 0}),
           routing_key="jobs"
        )
        logger.info("Job published to RabbitMQ.")

    except Exception as e:
        logger.error(f"Failed to publish job to RabbitMQ: {e}")
