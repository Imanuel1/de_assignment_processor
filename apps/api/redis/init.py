
import redis.asyncio as redis

from apps.api.common.constants import get_config

redis_client = None
def init_redis():
    try:
        global redis_client
        config = get_config()
        redis_client = redis.from_url(f"redis://{config.REDIS_USER}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}", decode_responses=True)
    except Exception as e:
        print(f"Error initializing Redis: {e}")
        raise e

def get_redis_client() -> redis.Redis:
    return redis_client