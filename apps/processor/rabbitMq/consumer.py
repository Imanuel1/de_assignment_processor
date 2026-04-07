import json
import logging

import aio_pika

from apps.processor.common.constants import get_config
from apps.processor.pg.model import JobTable
from apps.processor.pg.utils import is_job_canceled, update_table
from apps.processor.process.mapping import process_job_by_type
logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)
CONSTANT_DELAY = 1

async def consume_jobs(queue):
    await queue.consume(process_job)


async def process_job(message: aio_pika.IncomingMessage):
    config = get_config()
    async with message.process(requeue=False):
        payload = json.loads(message.body.decode())
        headers = message.headers or {}
        attempt = headers.get("x-retry-count", 0)
        logging.info(f"Processing job - {payload.get('idempotency_key')}. Attempt: {attempt}")
        
        try:
            if is_job_canceled(payload.get('idempotency_key')):
                logging.info(f"Job - {payload.get('idempotency_key')}: Canceled. Skipping...")
                return

            logging.info(f"Job - {payload.get('idempotency_key')}: Processing...")
            job_type = payload.get("job_type")
            job_data = payload.get("payload")
            result = process_job_by_type(job_type, job_data)

            updated_data = {"status": "completed", "result": result}
            update_table(JobTable, updated_data, payload.get('idempotency_key'))
            #no need manual ack its handled by the context manager, if no exception is raised, the message will be acked, if an exception is raised, the message will be rejected and requeued based on the retry logic implemented in the except block
            # await message.ack()
            
        except Exception as e:
            if attempt < config.RABBITMQ_MAX_RETRIES:
                # exponentially delay - constant * 2^attempt
                delay = CONSTANT_DELAY * (2 ** attempt)
                logging.warning(f"Error processing job - {payload.get('idempotency_key')}: {e}. Retrying in {delay}s...")
                                
                new_headers = dict(headers)
                new_headers["x-retry-count"] = f"{int(attempt) + 1}"
                expiration_time = f"{delay * 1000}"
                body_as_bytes = message.body if isinstance(message.body, bytes) else message.body.encode()

                await message.channel.basic_publish(
                    body=body_as_bytes,
                    routing_key=message.routing_key,
                    properties=aio_pika.Message(
                        body=body_as_bytes,
                        expiration=expiration_time,
                        headers=new_headers,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    )
                )
            else:
                logging.error(f"Job - {payload.get('idempotency_key')}: Max retries reached. Dropping message.")
                await message.reject(requeue=False)
                #TODO: what kind of dead letter queue logic we want to implement here? for now, we just reject the message and log the error.
                #maybe another table in the database to store the failed jobs for future analysis? or a notification system to alert the team when a job fails after max retries?

                updated_data = {"status": "failed", "result": None, "error": str(e)}
                update_table(JobTable, updated_data, payload.get('idempotency_key'))