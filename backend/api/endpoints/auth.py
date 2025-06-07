import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session
from backend.services.crud import user_crud
from backend.schemas.user import UserCreate, UserSchema
from backend.core.config import settings
from backend.api.auth_utils import verify_telegram_auth, is_payload_fresh

router = APIRouter(prefix="/api/auth")
logger = logging.getLogger(__name__)

# полный список админ‐ID из конфига
ADMIN_TELEGRAM_IDS = settings.ADMIN_TG_IDS


@router.post("/login", response_model=UserSchema)
async def login(
    response: Response,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(db_session),
):
    logger.info("🔑 Попытка логина через Telegram-payload: %s", payload)

    # 1) проверяем hash
    if not verify_telegram_auth(payload):
        logger.warning("❌ Неверный hash от Telegram: %s", payload.get("hash"))
        raise HTTPException(400, "Invalid Telegram hash")

    # 2) проверяем свежесть
    if not is_payload_fresh(payload, window=300):
        logger.warning("❌ Устаревший auth_date: %s", payload.get("auth_date"))
        raise HTTPException(400, "Expired Telegram login")

    # 3) вынимаем id/username
    try:
        tg_id = int(payload["id"])
        tg_username = payload.get("username", "")
    except (KeyError, ValueError):
        raise HTTPException(400, "Telegram ID обязателен")

    user_in = UserCreate(telegram_id=tg_id, username=tg_username)

    # 4) upsert + is_admin
    existing = await user_crud.get_by_telegram_id(db, telegram_id=tg_id)
    if existing is None:
        is_admin = tg_id in ADMIN_TELEGRAM_IDS
        user_obj = await user_crud.create(
            db, obj_in=user_in, extra_fields={"is_admin": is_admin}
        )
        logger.info("✅ Новый пользователь: %s", user_obj.username)
    else:
        user_obj = existing
        logger.info("🔄 Уже в БД: %s", user_obj.username)

    # 5) ставим cookie
    response.set_cookie(
        "tg_id",
        str(tg_id),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )

    return user_obj


@router.get("/user/{telegram_id}", response_model=UserSchema)
async def get_user(
    telegram_id: int,
    db: AsyncSession = Depends(db_session),
):
    logger.info("📌 Профиль ID=%s", telegram_id)
    user = await user_crud.get_by_telegram_id(db, telegram_id=telegram_id)
    if user is None:
        logger.warning("❌ Не найден: %s", telegram_id)
        raise HTTPException(404, "Пользователь не найден")
    return user


async def get_current_user(
    tg_id: str | None = Cookie(None, alias="tg_id"),
    db: AsyncSession = Depends(db_session),
) -> UserSchema:
    if tg_id is None:
        raise HTTPException(401, "Не авторизован")
    try:
        tg_id_val = int(tg_id)
    except ValueError:
        raise HTTPException(401, "Неправильный tg_id в cookie")

    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id_val)
    if user is None:
        raise HTTPException(401, "Пользователь не авторизован")
    return user


@router.get("/me", response_model=UserSchema)
async def read_own_profile(current_user: UserSchema = Depends(get_current_user)):
    return current_user
