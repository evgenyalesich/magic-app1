from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.core.config import settings
from sqlalchemy.pool import NullPool

# Single async engine used across the app
engine = create_async_engine(settings.DATABASE_URL, echo=True, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
