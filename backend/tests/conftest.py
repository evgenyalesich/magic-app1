import asyncio
import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.core.database import async_session


# ───────── event-loop для pytest-asyncio ─────────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ───────── фикстура «чистая сессия БД» ───────────
@pytest_asyncio.fixture
async def async_session_fixture():
    async with async_session() as session:
        async with session.begin():
            yield session          # тест использует session …
            await session.rollback()  # … и всё откатывается


# ───────── httpx.AsyncClient, работающий in-memory ─────────
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
