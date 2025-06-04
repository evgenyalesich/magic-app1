from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db


async def db_session(session: AsyncSession = Depends(get_db)):
    return session
