import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import unquote_plus

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session
from backend.api.auth_utils import is_payload_fresh, verify_telegram_auth
from backend.core.config import settings
from backend.schemas.user import UserCreate, UserSchema
from backend.services.crud import user_crud

log = logging.getLogger(__name__)
router = APIRouter(tags=["Auth"])

_ADMIN_IDS = set(settings.ADMIN_TELEGRAM_IDS)
_IS_HTTPS = str(settings.FRONTEND_ORIGIN).startswith("https://")


# ─────────────────────────  /login  ──────────────────────────
@router.post("/login", response_model=UserSchema)
async def login(
    payload: Dict[str, Any] = Body(...),
    response: Response = Response(),
    db: AsyncSession = Depends(db_session),
):
    log.info("🔑 [/login] raw payload = %s", payload)

    # 1) пришёл Web-App initData
    if "init_data" in payload:
        raw_init = payload["init_data"]

        # разбираем строку «k=v&k=v…» в словарь
        init_params: Dict[str, str] = {}
        for part in raw_init.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                init_params[k] = unquote_plus(v)
        log.debug("Parsed raw init_data params: %s", init_params)

        # валидируем подпись и свежесть
        if not verify_telegram_auth(init_params):
            raise HTTPException(400, "Invalid Telegram hash")
        if not is_payload_fresh(init_params):
            raise HTTPException(400, "Expired auth_date")

        # извлекаем user-объект
        try:
            user_obj = json.loads(init_params.get("user", "{}"))
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid user JSON")

        payload = {
            "telegram_id": user_obj.get("id"),
            "username": user_obj.get("username", ""),
        }

    # 2) вызов из бота (bot-register) — telegram_id уже в payload
    tg_id_raw = payload.get("telegram_id") or payload.get("id")
    if tg_id_raw is None:
        raise HTTPException(400, "telegram_id missing")

    try:
        tg_id = int(tg_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(400, "Bad telegram id type")

    username = str(payload.get("username", ""))

    # создаём / обновляем пользователя
    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id)
    if user is None:
        user = await user_crud.create(
            db,
            obj_in=UserCreate(telegram_id=tg_id, username=username),
            extra_fields={"is_admin": tg_id in _ADMIN_IDS},
        )
        log.info("✅ [/login] new user created: %s", username)
    else:
        log.info("🔄 [/login] existing user: tg_id=%s user=%s", tg_id, username)

    # ставим cookie
    response.set_cookie(
        "tg_id",
        str(tg_id),
        httponly=True,
        secure=_IS_HTTPS,
        samesite="none" if _IS_HTTPS else "lax",
        max_age=7 * 24 * 3600,
    )
    return user


# ───────────────────────────  /me  ───────────────────────────
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


# ────────────────────────  /bot-register  ─────────────────────
@router.post("/bot-register", response_model=UserSchema)
async def bot_register(
    payload: Dict[str, Any],
    response: Response,
    db: AsyncSession = Depends(db_session),
):
    # переиспользуем логику /login
    return await login(payload=payload, response=response, db=db)
