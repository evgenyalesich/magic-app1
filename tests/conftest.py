# tests/conftest.py

import pytest_asyncio

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.core.config import DATABASE_URL
from backend.models.base import Base


# Убираем "+asyncpg", чтобы создать синхронный движок
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")


@pytest_asyncio.fixture
async def async_session_fixture():
    # 1) Синхронно создаём таблицы в базе, на которую указывает SYNC_DATABASE_URL
    sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
    Base.metadata.create_all(sync_engine)

    # 2) Заводим асинхронный движок
    async_engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

    # 3) Открываем асинхронную сессию
    async with AsyncSessionLocal() as session:
        yield session

    # 4) После теста закрываем асинхронный движок
    await async_engine.dispose()

    # 5) Дропаем все таблицы (опционально)
    Base.metadata.drop_all(sync_engine)
