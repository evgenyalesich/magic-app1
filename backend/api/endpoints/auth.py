import logging
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session
from backend.services.crud import user_crud
from backend.schemas.user import UserCreate, UserSchema
from backend.core.config import settings
from backend.api.auth_utils import verify_telegram_auth, is_payload_fresh

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])

# Админские ID
ADMIN_TELEGRAM_IDS: List[int] = settings.ADMIN_TELEGRAM_IDS


@router.post("/login", response_model=UserSchema)
async def login(
    response: Response,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(db_session),
):
    logger.info("🔑 Попытка логина через Telegram-payload: %s", payload)

    # Проверка hash (Telegram Login Widget)
    if not verify_telegram_auth(payload):
        logger.warning("❌ Неверный hash от Telegram: %s", payload.get("hash"))
        raise HTTPException(status_code=400, detail="Invalid Telegram hash")

    # Проверка свежести (auth_date)
    if not is_payload_fresh(payload, window=300):
        logger.warning("❌ Устаревший auth_date: %s", payload.get("auth_date"))
        raise HTTPException(status_code=400, detail="Expired Telegram login")

    # Извлечение данных
    try:
        tg_id = int(payload["id"])
        tg_username = payload.get("username", "")
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Telegram ID обязателен")

    user_in = UserCreate(telegram_id=tg_id, username=tg_username)
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

    # Ставим cookie для авторизации
    response.set_cookie(
        key="tg_id",
        value=str(tg_id),
        httponly=True,
        secure=False,  # в продакшене True
        samesite="lax",
        max_age=7 * 24 * 3600,
    )
    return user_obj


async def get_current_user(
    tg_id: str | None = Cookie(None, alias="tg_id"),
    db: AsyncSession = Depends(db_session),
) -> UserSchema:
    if tg_id is None:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        tg_id_val = int(tg_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неправильный tg_id в cookie")

    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id_val)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")
    return user


@router.get("/me", response_model=UserSchema)
async def read_own_profile(current_user: UserSchema = Depends(get_current_user)):
    return current_user


@router.post("/bot-register", response_model=UserSchema)
async def bot_register(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(db_session),
):
    """
    Используется ботом для upsert без проверки hash
    Ожидает JSON: { telegram_id, username }
    """
    tg_id = payload.get("telegram_id")
    if not tg_id:
        raise HTTPException(status_code=400, detail="telegram_id обязателен")
    user_obj = await user_crud.upsert(
        db,
        telegram_id=int(tg_id),
        username=payload.get("username", ""),
    )
    return user_obj
