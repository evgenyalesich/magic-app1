# backend/api/deps.py

import logging
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db as _get_db
from backend.services.crud import user_crud
from backend.models import User

logger = logging.getLogger(__name__)


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Депенденси для получения сессии с БД.
    """
    async for session in _get_db():
        yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(db_session),
) -> User:
    """
    Депенденси для получения текущего пользователя по куке 'tg_id'.
    """
    tg_id_cookie = request.cookies.get("tg_id")
    if not tg_id_cookie:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        tg_id_val = int(tg_id_cookie)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный tg_id в cookie")

    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id_val)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


async def admin_guard(
    user: User = Depends(get_current_user),
) -> User:
    """
    Депенденси, который проверяет, что текущий пользователь — админ.
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return user
