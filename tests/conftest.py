# tests/conftest.py

import pytest_asyncio

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.core.config import DATABASE_URL
from backend.models.base import Base

# Убираем "+asyncpg" из URL, чтобы получить чистый синхронный URL
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")


@pytest_asyncio.fixture
async def async_session_fixture():
    # 1) Синхронно создаём таблицы через обычный (синхронный) движок
    sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
    Base.metadata.create_all(sync_engine)

    # 2) Заводим для этого теста свой собственный AsyncEngine
    async_engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

    # 3) Открываем асинхронную сессию и передаём её в тест
    async with AsyncSessionLocal() as session:
        yield session

    # 4) После теста: сначала закрываем асинхронный движок (он сам «отпустит» соединения)
    await async_engine.dispose()

    # 5) И только затем дропаем все таблицы через синхронный движок
    Base.metadata.drop_all(sync_engine)
