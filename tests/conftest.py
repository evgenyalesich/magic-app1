import asyncio, pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from backend.main import app
from backend.core.database import async_session

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# ─── чистая сессия ─────────────────────────────────
@pytest_asyncio.fixture
async def async_session_fixture():
    async with async_session() as session:
        yield session
        await session.rollback()

# ─── авто-truncate перед каждым тестом ─────────────
@pytest_asyncio.fixture(autouse=True)
async def clean_db(async_session_fixture):
    tables = (
        "order_items", "orders",
        "products", "categories",
        "messages", "users",
    )
    for t in tables:
        await async_session_fixture.execute(text(f"TRUNCATE {t} CASCADE"))
    await async_session_fixture.commit()

# ─── httpx клиент ─────────────────────────────────
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

