import json
import logging

import aio_pika
from fastapi import FastAPI

from apps.api.common.enum import JobStatus
from apps.api.pg.model import JobTable
from apps.api.pg.utils import update_table
from apps.api.rabbitMq.utils import calculate_delay_ms
from apps.api.schemas.jobRequest import JobRequest
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def publish_job_to_rabbitmq(app: FastAPI, job_data: dict, priority: int = 1):
    try:
        schdule_time = job_data.get("scheduled_time")
        if schdule_time:
            schdule_time = schdule_time.isoformat()
            job_data["scheduled_time"] = schdule_time
            update_table(app.state.db_session_factory(), JobTable, {"status": JobStatus.SCHEDULED.value}, job_data["idempotency_key"])

        body = json.dumps(job_data)
        expiration_time = calculate_delay_ms(schdule_time)
        logger.info(f"Publishing job to RabbitMQ: {body}, priority: {priority}, schedule_time: {schdule_time}")

        await app.state.channel.default_exchange.publish(
            aio_pika.Message(
                body=body.encode(),
                priority=priority,
                expiration_time=expiration_time,
                # expiration=expiration_time,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT, 
                headers={"x-retry-count": 0}),
            # expiration_time=expiration_time,
            routing_key="jobs"
        )
        logger.info("Job published to RabbitMQ.")

    except Exception as e:
        logger.error(f"Failed to publish job to RabbitMQ: {e}")
