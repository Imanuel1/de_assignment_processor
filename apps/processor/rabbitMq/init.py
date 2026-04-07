import logging
import aio_pika
from apps.api.common.constants import get_config
from apps.processor.rabbitMq.consumer import consume_jobs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_rabbitmq():
    try:
        config = get_config()
        connection = await aio_pika.connect_robust(f"amqp://{config.RABBITMQ_USER}:{config.RABBITMQ_PASS}@{config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}/")
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue("jobs", arguments={"x-max-priority": config.RABBITMQ_QUEUE_PRIORITY}, durable=True)
        logger.info("RabbitMQ connection established and queue declared.")
        await consume_jobs(queue)
        return connection

    except Exception as e:
        logger.error(f"Failed to initialize RabbitMQ: {e}")
        raise e

