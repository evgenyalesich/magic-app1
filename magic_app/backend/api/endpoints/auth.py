from __future__ import annotations

"""Endpoints that handle Telegram Web-App authentication."""

import logging
from typing import Dict, Optional
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# ── Internal imports ──────────────────────────────────────────────────
from backend.core.config import settings
from backend.api.deps import get_db_session, get_current_user
from backend.models.user import User
from backend.schemas.user import UserSchema
from backend.services.crud import user_crud
from backend.utils.auth_manager import get_telegram_auth_manager

# ─────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
router = APIRouter(tags=["Auth"])

LAST_INIT_DATA: Dict[str, Optional[str]] = {"data": None}

telegram_auth_manager = get_telegram_auth_manager(
    bot_token=settings.TELEGRAM_BOT_TOKEN,
    timeout_sec=60 * 60 * 24,
)

# ----------------------------------------------------------------------------
# 2. Pydantic payloads / responses
# ----------------------------------------------------------------------------
class InitDataPayload(BaseModel):
    init_data: str = Field(..., description="Строка initData от Telegram Web-App")

# Используем эту модель, чтобы ответ соответствовал ожиданиям фронтенда { "user": ... }
class AuthResponse(BaseModel):
    user: UserSchema


# ----------------------------------------------------------------------------
# 3. Endpoints
# ----------------------------------------------------------------------------
@router.post("/login", response_model=AuthResponse)
async def login_webapp(
    payload: InitDataPayload,
    db: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    """Login / register via Telegram Web-App *initData*."""
    logger.info("--- [AUTH /login] Начат процесс входа ---")

    init_data_raw = payload.init_data
    # --- НОВЫЙ ЛОГ ---
    logger.info("[AUTH /login] Получены сырые данные: initData = %s", init_data_raw)
    LAST_INIT_DATA["data"] = init_data_raw

    # --- НОВЫЙ ЛОГ ---
    # Попробуем извлечь hash для наглядности в логах
    try:
        data_dict = dict(pair.split("=") for pair in init_data_raw.split("&"))
        received_hash = data_dict.get("hash", "Хэш не найден")
        logger.info("[AUTH /login] Извлечённый хэш для проверки: %s", received_hash)
    except Exception:
        logger.warning("[AUTH /login] Не удалось распарсить initData для извлечения хэша.")


    # 1. Валидация через наш auth_manager, который использует telegram-webapp-auth
    # --- НОВЫЙ ЛОГ ---
    logger.info("[AUTH /login] >> Вызов telegram_auth_manager.authenticate...")
    is_valid, user_info = telegram_auth_manager.authenticate(init_data_raw)
    # --- НОВЫЙ ЛОГ ---
    logger.info(
        "[AUTH /login] << Результат от auth_manager: is_valid=%s, user_info=%s",
        is_valid,
        user_info
    )

    if not is_valid:
        # --- НОВЫЙ ЛОГ ---
        logger.error("[AUTH /login] ПРОВАЛ ВАЛИДАЦИИ. Данные недействительны. Отказ в доступе.")
        raise HTTPException(status_code=401, detail="Невалидные данные Telegram Web-App.")

    if not user_info or "id" not in user_info:
        # --- НОВЫЙ ЛОГ ---
        logger.error("[AUTH /login] ПРОВАЛ. В данных отсутствует 'id' пользователя. Отказ в доступе.")
        raise HTTPException(status_code=401, detail="Не удалось извлечь user.id из initData")

    # 2. Поиск или создание пользователя в нашей базе данных
    user_tg_id = user_info["id"]
    user_username = user_info.get("username", "N/A")
    # --- НОВЫЙ ЛОГ ---
    logger.info(
        "[AUTH /login] Данные прошли проверку. Работа с пользователем: telegram_id=%s, username=%s",
        user_tg_id,
        user_username
    )

    user = await user_crud.get_or_create_user(
        db,
        telegram_id=user_tg_id,
        username=user_username,
        first_name=user_info.get("first_name", ""),
        last_name=user_info.get("last_name", ""),
    )
    # --- НОВЫЙ ЛОГ ---
    logger.info("[AUTH /login] Пользователь успешно найден/создан в БД: ID=%s", user.id)

    # Формируем и логгируем финальный ответ перед отправкой
    response_data = AuthResponse(user=UserSchema.from_orm(user))
    # --- НОВЫЙ ЛОГ ---
    logger.info("[AUTH /login] Отправка ответа на фронтенд: %s", response_data.json())
    logger.info("--- [AUTH /login] Процесс входа успешно завершён ---")

    return response_data


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    """Return current authenticated user."""
    return UserSchema.from_orm(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> Response:
    """Client-side only – серверных сессий нет."""
    logger.info("[AUTH /logout] /logout called – nothing to clean")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------------------------------------------------------------------------
# 4. /debug-crypto – only for DEV
# ----------------------------------------------------------------------------
@router.get("/debug-crypto", include_in_schema=False)
def debug_crypto_info():
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=404, detail="Endpoint disabled in production")

    init_data = LAST_INIT_DATA["data"]
    if not init_data:
        raise HTTPException(status_code=400, detail="Сначала выполните POST /login")

    # reconstruct data_check_string
    received_hash: Optional[str] = None
    pairs: list[tuple[str, str]] = []
    for pair in init_data.split("&"):
        if "=" not in pair:
            continue
        key, raw_val = pair.split("=", 1)
        if key == "hash":
            received_hash = raw_val
            continue
        pairs.append((key, unquote(raw_val)))

    pairs.sort(key=lambda kv: kv[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in pairs)

    ok, parsed_user = telegram_auth_manager.authenticate(init_data)

    return {
        "match": ok,
        "client_hash": received_hash,
        "server_hash": "Matches client_hash" if ok else "Validation failed",
        "data_check_string": data_check_string.split("\n"),
        "parsed_user_data_by_lib": parsed_user,
        "init_data_raw": init_data,
    }
