# backend/api/endpoints/auth.py

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.services.crud import user_crud
from backend.schemas.user import UserCreate, UserSchema
from backend.core.config import settings
from backend.api.auth_utils import verify_telegram_auth, is_payload_fresh

router = APIRouter()
logger = logging.getLogger(__name__)

# Берём из настроек полный список админ‐ID
ADMIN_TELEGRAM_IDS = settings.ADMIN_TG_IDS


@router.post("/login", response_model=UserSchema)
async def login(
    request: Request,
    response: Response,
    payload: Dict[str, Any],  # ожидаем JSON с Telegram‐параметрами
    db: AsyncSession = Depends(get_current_user),
):
    """
    Эндпоинт для «логина через Telegram-WebApp». Принимает JSON, который присылает
    Telegram Login Widget: id, username, auth_date, hash, ….

    Проверяем:
      1) валидность hash (через BOT_TOKEN);
      2) что auth_date «свежий» (не старше 5 минут);
      3) upsert пользователя: если есть telegram_id — возвращаем, иначе создаём.
      4) Пишем is_admin=True, если telegram_id входит в ADMIN_TELEGRAM_IDS.

    В ответ кладём юзера и ставим cookie с `tg_id`.
    """

    logger.info("🔑 Попытка логина через Telegram-payload: %s", payload)

    # 1) Проверяем, что hash корректен:
    if not verify_telegram_auth(payload):
        logger.warning("❌ Неверный hash от Telegram: %s", payload.get("hash"))
        raise HTTPException(status_code=400, detail="Invalid Telegram hash")

    # 2) Проверяем, что auth_date не слишком старый (opt):
    if not is_payload_fresh(payload, window=300):
        logger.warning("❌ Устаревший auth_date: %s", payload.get("auth_date"))
        raise HTTPException(status_code=400, detail="Expired Telegram login")

    # 3) Берём поля, которые нужны Pydantic-схеме UserCreate (telegram_id и username)
    try:
        tg_id = int(payload["id"])
        tg_username = payload.get("username", "")
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Telegram ID обязателен")

    user_in = UserCreate(telegram_id=tg_id, username=tg_username)

    # 4) Ищем в БД; если не нашли — создаём. Помечаем is_admin, если telegram_id в ADMIN_TELEGRAM_IDS
    existing_user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id)
    if not existing_user:
        is_admin_flag = tg_id in ADMIN_TELEGRAM_IDS
        # Передаём в create() Pydantic-модель и доп.поле is_admin
        user_obj = await user_crud.create(
            db,
            obj_in=user_in,
            extra_fields={"is_admin": is_admin_flag},
        )
        logger.info("✅ Новый пользователь зарегистрирован: %s", user_obj.username)
    else:
        user_obj = existing_user
        logger.info("🔄 Пользователь уже есть в БД: %s", user_obj.username)

    # 5) Ставим cookie с telegram_id (тип «мягкая авторизация»)
    #    По желанию можете использовать Secure+HttpOnly+SameSite опции
    response.set_cookie(
        key="tg_id",
        value=str(tg_id),
        httponly=True,
        secure=False,  # или True, если HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 дней
    )

    return user_obj


@router.get("/user/{telegram_id}", response_model=UserSchema)
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_current_user)):
    logger.info("📌 Запрос профиля пользователя с ID=%s", telegram_id)
    user = await user_crud.get_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        logger.warning("❌ Пользователь с Telegram ID=%s не найден", telegram_id)
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


async def get_current_user(
    tg_id_cookie: str = Request.cookies.get,  # автоматически FastAPI найдёт cookie tg_id
    db: AsyncSession = Depends(get_current_user),
) -> UserSchema:
    """
    Зависимость, возвращающая текущего пользователя:
    берём cookie 'tg_id', ищем в БД. Если не нашли — 401.
    """

    # Если cookie вообще нет
    if not tg_id_cookie("tg_id"):
        raise HTTPException(status_code=401, detail="Не авторизован")

    try:
        tg_id_val = int(tg_id_cookie("tg_id"))
    except ValueError:
        raise HTTPException(status_code=401, detail="Неправильный tg_id в cookie")

    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id_val)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")
    return user
