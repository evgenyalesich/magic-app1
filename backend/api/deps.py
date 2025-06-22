"""
backend/dependencies.py
~~~~~~~~~~~~~~~~~~~~~~
Единые зависимости FastAPI-слоя.

* ``get_db``           – асинхронная сессия БД (обёртка над core.database.get_db)
* ``get_current_user`` – находит (или создаёт) пользователя по Telegram-id,
                         который берём из **заголовка / query-param / cookie**
* ``admin_guard``      – убеждаемся, что ``user.is_admin`` = True
"""
from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Header, Query, Cookie, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db as _core_get_db
from backend.models import User
from backend.services.crud import user_crud

# ──────────────────────────────
# 1. DB-session
# ──────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency-обёртка над ``core.database.get_db``.
    Используйте во всех энд-пойнтах:

        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async for session in _core_get_db():
        yield session


# Back-compat alias ― пусть старый код не ломается
db_session = get_db


# ──────────────────────────────
# 2. Authentication helpers
# ──────────────────────────────
async def _extract_telegram_id(
    # 1) production-вариант – заголовок от Web-App / Bot API
    x_telegram_id: int | None = Header(default=None, alias="X-Telegram-Id"),

    # 2) отладка в браузере / Postman
    tg_id_query: int | None = Query(default=None, alias="tg_id"),

    # 3) fallback – cookie (старое веб-приложение)
    tg_id_cookie: int | None = Cookie(default=None, alias="tg_id"),
) -> int:
    """Пытаемся достать tg-id из всех доступных источников."""
    telegram_id = x_telegram_id or tg_id_query or tg_id_cookie
    if telegram_id is None:
        raise HTTPException(status_code=401, detail="Telegram-id missing")
    return telegram_id


async def get_current_user(
    telegram_id: int = Depends(_extract_telegram_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Возвращает *существующего* пользователя **или** создаёт запись «на лету».

    ➜ Не надо отдельно регистрировать пользователей –
       достаточно передать корректный ``telegram_id``.
    """
    # get_or_create — мы добавили в CRUDBase раньше
    user = await user_crud.get_or_create(db, telegram_id=telegram_id)
    return user


async def admin_guard(
    user: User = Depends(get_current_user),
) -> User:
    """
    Dependency-фильтр: пропускает только админов.

        @router.get("/admin-only", dependencies=[Depends(admin_guard)])
        async def secret_route():
            ...
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


__all__ = [
    "get_db",
    "db_session",
    "get_current_user",
    "admin_guard",
]
