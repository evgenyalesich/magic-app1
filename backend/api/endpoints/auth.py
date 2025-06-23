import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session
from backend.api.auth_utils import create_telegram_auth
from backend.core.config import settings
from backend.schemas.user import UserCreate, UserSchema
from backend.services.crud import user_crud


log = logging.getLogger(__name__)
router = APIRouter(tags=["Auth"])

ADMIN_IDS = set(settings.ADMIN_TELEGRAM_IDS)
IS_HTTPS = getattr(settings.FRONTEND_ORIGIN, "scheme", "").lower() == "https"


@router.post("/login", response_model=UserSchema)
async def login(
    payload: Dict[str, Any] = Body(...),
    response: Response = Response(),
    db: AsyncSession = Depends(db_session),
):
    log.info("[/login] payload = %r", payload)

    # Если пришёл WebApp initData — выдираем user
    if "init_data" in payload:
        raw = payload["init_data"]
        auth = create_telegram_auth()
        user_data = auth.extract_user(raw)
        if not user_data:
            raise HTTPException(400, "Cannot parse Telegram user data")

        payload = {
            "telegram_id": user_data.get("id"),
            "username": user_data.get("username", ""),
        }
        log.debug("Parsed user_data: %r", payload)

    # Теперь payload содержит telegram_id
    tg_id_raw = payload.get("telegram_id") or payload.get("id")
    if tg_id_raw is None:
        raise HTTPException(400, "telegram_id missing")
    try:
        tg_id = int(tg_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(400, "Bad telegram_id type")

    username = str(payload.get("username", ""))

    # Создаём или обновляем пользователя
    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id)
    if user is None:
        user = await user_crud.create(
            db,
            obj_in=UserCreate(telegram_id=tg_id, username=username),
            extra_fields={"is_admin": tg_id in ADMIN_IDS},
        )
        log.info("Created new user %s (%s)", username, tg_id)
    else:
        log.info("Existing user %s (%s)", username, tg_id)

    # Ставим куки
    response.set_cookie(
        "tg_id",
        str(tg_id),
        httponly=True,
        secure=IS_HTTPS,
        samesite="none" if IS_HTTPS else "lax",
        max_age=7 * 24 * 3600,
    )
    return user


@router.get("/me", response_model=UserSchema)
async def me(
    tg_id: Optional[str] = Cookie(None, alias="tg_id"),
    db: AsyncSession = Depends(db_session),
):
    if tg_id is None:
        raise HTTPException(401, "Not authorised")
    try:
        tg_id_int = int(tg_id)
    except (TypeError, ValueError):
        raise HTTPException(401, "Invalid tg_id cookie")

    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id_int)
    if not user:
        raise HTTPException(401, "User not found")
    return user


@router.post("/bot-register", response_model=UserSchema)
async def bot_register(
    payload: Dict[str, Any] = Body(...),
    response: Response = Response(),
    db: AsyncSession = Depends(db_session),
):
    # Просто переиспользуем логику /login
    return await login(payload=payload, response=response, db=db)


@router.post("/debug/auth")
async def debug_auth(payload: Dict[str, Any] = Body(...)):
    raw = payload.get("init_data")
    if not raw:
        return {"error": "No init_data provided"}

    params = dict(parse_qsl(raw, keep_blank_values=True))
    return {
        "raw_init_data": raw,
        "parsed_params": params,
        "parsed_user": params.get("user"),
    }
