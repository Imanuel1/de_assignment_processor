import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from apps.api.pg.init import get_db
from apps.api.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def initialize_app():
    from apps.api.pg.init import init_db
    from apps.api.rabbitMq.init import init_rabbitmq
    from apps.api.redis.init import init_redis
    
    init_db(app)
    init_redis()
    await init_rabbitmq(app)
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
# Use AsyncClient with the app directly
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac