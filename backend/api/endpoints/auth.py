import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session
from backend.api.auth_utils import verify_telegram_auth, is_payload_fresh
from backend.core.config import settings
from backend.schemas.user import UserCreate, UserSchema
from backend.services.crud import user_crud

log = logging.getLogger(__name__)
router = APIRouter(tags=["Auth"])

_ADMIN_IDS = set(settings.ADMIN_TELEGRAM_IDS)
_IS_HTTPS = str(settings.FRONTEND_ORIGIN).startswith("https://")


# ── /login ─────────────────────────────────────────────────────
@router.post("/login", response_model=UserSchema)
async def login(
    payload: Dict[str, Any] = Body(...),
    response: Response = Response(),
    db: AsyncSession = Depends(db_session),
):
    log.info("🔑 [/login] raw payload = %s", payload)

    is_bot_call = "hash" not in payload
    if not is_bot_call:
        if not verify_telegram_auth(payload):
            raise HTTPException(400, "Invalid Telegram hash")
        if not is_payload_fresh(payload):
            raise HTTPException(400, "Expired auth_date")

    tg_id_raw: Optional[Any] = payload.get("id") or payload.get("telegram_id")
    if tg_id_raw is None:
        raise HTTPException(400, "telegram_id missing")

    try:
        tg_id = int(tg_id_raw)
    except ValueError:
        raise HTTPException(400, "Bad telegram id type")

    username = str(payload.get("username", ""))

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

    response.set_cookie(
        "tg_id",
        str(tg_id),
        httponly=True,
        secure=_IS_HTTPS,
        samesite="none" if _IS_HTTPS else "lax",
        max_age=7 * 24 * 3600,
    )
    return user


# ── /me ────────────────────────────────────────────────────────
@router.get("/me", response_model=UserSchema)
async def me(
    tg_id: Optional[str] = Cookie(None, alias="tg_id"),
    db: AsyncSession = Depends(db_session),
):
    if tg_id is None:
        raise HTTPException(401, "Not authorised")

    try:
        tg_id_int = int(tg_id)
    except ValueError:
        raise HTTPException(401, "Invalid tg_id cookie")

    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id_int)
    if user is None:
        raise HTTPException(401, "User not found")
    return user


# ── /bot-register (aiogram) ────────────────────────────────────
@router.post("/bot-register", response_model=UserSchema)
async def bot_register(
    payload: Dict[str, Any],
    response: Response,
    db: AsyncSession = Depends(db_session),
):
    return await login(payload=payload, response=response, db=db)
