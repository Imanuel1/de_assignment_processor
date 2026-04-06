import asyncio
import json
import logging

import aio_pika

from apps.processor.common.constants import get_config
from apps.processor.pg.model import JobTable
from apps.processor.pg.utils import update_table
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
            
            #TODO: simulate job processing logic here. 
            logging.info(f"Job - {payload.get('idempotency_key')}: Processing...")
            # await message.ack()


            # For demonstration, we'll just raise an exception to trigger retries.
            
            raise Exception("Job failed!")
            
        except Exception as e:
            if attempt < config.RABBITMQ_MAX_RETRIES:
                # exponentially delay - constant * 2^attempt
                delay = CONSTANT_DELAY * (2 ** attempt)
                logging.warning(f"Error processing job - {payload.get('idempotency_key')}: {e}. Retrying in {delay}s...")
                
                await asyncio.sleep(delay)
                
                new_headers = dict(headers)
                new_headers["x-retry-count"] = f"{int(attempt) + 1}"

                body_as_bytes = message.body if isinstance(message.body, bytes) else message.body.encode()
                await message.channel.basic_publish(
                    body=body_as_bytes,
                    routing_key=message.routing_key,
                    properties=aio_pika.Message(
                        headers=new_headers,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    )
                )
            else:
                logging.error(f"Job - {payload.get('idempotency_key')}: Max retries reached. Dropping message.")
                await message.reject(requeue=False)
                #TODO: what kind of dead letter queue logic we want to implement here? for now, we just reject the message and log the error.
                
                updated_data = {"status": "failed", "result": None, "error": str(e)}
                update_table(JobTable.__tablename__, updated_data, payload.get('idempotency_key'))