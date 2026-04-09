

from functools import lru_cache
import logging
import sys

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "jobs"
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_QUEUE_PRIORITY: int = 10
    RABBITMQ_MAX_RETRIES: int = 3
    RABBITMQ_CONSTANT_DELAY: int = 3
    WEBHOOK_SUCCESS_RATE: int = 80


@lru_cache()
def get_config() -> Config:
    return Config()

try:
    get_config()
except ValidationError as e:
    logger.error(f"Error loading configuration: {e}")
    
    sys.exit(1)