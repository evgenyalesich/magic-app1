import pytest_asyncio
from backend.core.database import async_session, engine
from backend.models import Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Create all tables before tests and drop them afterwards."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session_fixture():  # переименуем, чтобы не путать
    async with async_session() as session:  # вызываем фабрику
        yield session
        await session.rollback()  # чистим изменения
