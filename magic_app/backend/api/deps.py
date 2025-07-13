# backend/api/deps.py
from __future__ import annotations

import logging
import os
from typing import AsyncGenerator, Set

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import get_db
from backend.models.user import User
from backend.services.crud import user_crud
from backend.utils.auth_manager import get_telegram_auth_manager

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# 0. Telegram auth manager (singleton)
# ----------------------------------------------------------------------------
telegram_auth_manager = get_telegram_auth_manager(
    bot_token=settings.TELEGRAM_BOT_TOKEN,
    timeout_sec=60 * 60 * 24,  # 24h – читается из settings при желании
)

# ----------------------------------------------------------------------------
# 1. Белый список администраторов
# ----------------------------------------------------------------------------
_raw = os.getenv("ADMIN_TELEGRAM_IDS") or os.getenv("ADMIN_IDS", "")
_ALLOWED_ADMIN_IDS: Set[int] = {int(tg_id) for tg_id in _raw.split(",") if tg_id.strip().isdigit()}
logger.info("[AUTH] Загружен whitelist админов: %s", _ALLOWED_ADMIN_IDS or "не задан")

# ----------------------------------------------------------------------------
# 2. Сессия к базе данных
# ----------------------------------------------------------------------------
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session

# ----------------------------------------------------------------------------
# 3. Current user dependency (Telegram initData)
# ----------------------------------------------------------------------------
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Authenticate each request via the `X-Telegram-Init-Data` header."""

    init_data_raw = request.headers.get("X-Telegram-Init-Data")
    if not init_data_raw:
        logger.warning("[AUTH] header X-Telegram-Init-Data missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не предоставлены данные Telegram WebApp.",
            headers={"WWW-Authenticate": "WebApp"},
        )

    # ------------------------------------------------------------------
    # Validate initData + upsert user
    # ------------------------------------------------------------------
    is_valid, user_info = telegram_auth_manager.authenticate(init_data_raw)
    if not is_valid:
        logger.warning("[AUTH] initData failed signature/TTL check")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидные данные Telegram WebApp.",
            headers={"WWW-Authenticate": "WebApp"},
        )

    if not user_info or "id" not in user_info:
        logger.warning("[AUTH] Could not extract telegram user id from initData: %s", user_info)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные пользователя в initData.",
            headers={"WWW-Authenticate": "WebApp"},
        )

    telegram_id = user_info["id"]
    username = user_info.get("username", "")
    first_name = user_info.get("first_name", "")
    last_name = user_info.get("last_name", "")

    try:
        user = await user_crud.get_or_create_user(
            db,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
    except Exception as exc:
        logger.error("[AUTH] DB error while upserting user %s: %s", telegram_id, exc, exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "DB error при аутентификации")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Учетная запись неактивна.")

    # Пометим админа, если в whitelist
    user.is_admin = user.telegram_id in _ALLOWED_ADMIN_IDS
    logger.info("[AUTH] OK: user %s authenticated (admin=%s)", telegram_id, user.is_admin)
    return user

# ----------------------------------------------------------------------------
# 4. Admin‑only dependency
# ----------------------------------------------------------------------------
async def admin_guard(user: User = Depends(get_current_user)) -> User:
    if _ALLOWED_ADMIN_IDS and user.telegram_id not in _ALLOWED_ADMIN_IDS:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required (whitelist)")
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required (is_admin flag)")
    return user

# ----------------------------------------------------------------------------
# 5. Exports
# ----------------------------------------------------------------------------
__all__ = [
    "get_db_session",
    "get_current_user",
    "admin_guard",
]
