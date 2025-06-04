import pytest_asyncio
from backend.core.database import async_session  # ← имя как в файле database.py


@pytest_asyncio.fixture
async def async_session_fixture():  # переименуем, чтобы не путать
    async with async_session() as session:  # вызываем фабрику
        yield session
        await session.rollback()  # чистим изменения
