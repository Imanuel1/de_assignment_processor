import asyncio
from datetime import datetime
import json
import logging

import aio_pika

from apps.processor.common.constants import get_config
from apps.processor.pg.model import JobTable
from apps.processor.pg.utils import is_job_canceled, update_table
from apps.processor.process.mapping import process_job_by_type
from apps.processor.common.enum import JobStatus
from functools import partial
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def consume_jobs(queue, channel):
    callback_with_chennel = partial(process_job, channel=channel)
    await queue.consume(callback_with_chennel)


async def process_job(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    from apps.processor.main import active_tasks
    #add the current task to the active tasks set, so that we can wait for it to finish before shutting down the application
    current_task = asyncio.current_task()
    active_tasks.add(current_task)

    try:    
        config = get_config()
        async with message.process(requeue=False):
            payload = json.loads(message.body.decode())
            headers = message.headers or {}
            attempt = headers.get("x-retry-count", 0)
            logger.info(f"Processing job - {payload.get('idempotency_key')}. Attempt: {attempt}")
            
            try:
                if is_job_canceled(payload.get('idempotency_key')):
                    logger.info(f"Job - {payload.get('idempotency_key')}: Canceled. Skipping...")
                    return

                updated_started_at = {"status": JobStatus.PROCESSING.value, "started_at": datetime.now()}
                update_table(JobTable, updated_started_at, payload.get('idempotency_key'))

                logger.info(f"Job - {payload.get('idempotency_key')}: Processing...")
                job_type = payload.get("job_type")
                job_data = payload.get("payload")
                result = process_job_by_type(job_type, job_data)

                updated_data = {"status": JobStatus.COMPLETED.value, "result": result, "completed_at": datetime.now()}
                update_table(JobTable, updated_data, payload.get('idempotency_key'))
                #no need manual ack its handled by the context manager, if no exception is raised, the message will be acked, if an exception is raised, the message will be rejected and requeued based on the retry logic implemented in the except block
                # await message.ack()
                
            except Exception as e:
                if attempt < config.RABBITMQ_MAX_RETRIES:
                    # exponentially delay - constant * 2^attempt
                    delay = int(config.RABBITMQ_CONSTANT_DELAY) * (2 ** attempt)
                    logger.warning(f"Error processing job - {payload.get('idempotency_key')}: {e}. Retrying in {delay}s...")

                    new_headers = dict(headers)
                    new_headers["x-retry-count"] = int(attempt) + 1
                    new_headers["x-delay"] = delay * 1000
                    body_as_bytes = message.body if isinstance(message.body, bytes) else message.body.encode()
                    
                    delayed_exchange = await channel.declare_exchange(
                        "delayed_jobs_exchange", 
                        type="x-delayed-message", 
                        passive=True
                    )

                    await delayed_exchange.publish(
                        aio_pika.Message(
                            priority=message.priority,
                            body=body_as_bytes,
                            headers=new_headers,
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                        ),
                        routing_key=message.routing_key
                    )
                else:
                    logger.error(f"Job - {payload.get('idempotency_key')}: Max retries reached. Dropping message.")
                    #TODO: what kind of dead letter queue logic we want to implement here? for now, we just reject the message and log the error.
                    #maybe another table in the database to store the failed jobs for future analysis? or a notification system to alert the team when a job fails after max retries?

                    updated_data = {"status": JobStatus.FAILED.value, "result": None, "error": str(e)}
                    update_table(JobTable, updated_data, payload.get('idempotency_key'))
    finally:
        active_tasks.discard(current_task)