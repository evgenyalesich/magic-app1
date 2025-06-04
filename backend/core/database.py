from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.core.config import DATABASE_URL
from sqlalchemy.pool import NullPool

engine = create_async_engine(DATABASE_URL, echo=True)
engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
