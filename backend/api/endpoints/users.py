# backend/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.core.config import settings        # <-- NEW
from backend.schemas.user import UserSchema, UserCreate
from backend.services.crud import user_crud

router = APIRouter(prefix="/users", tags=["Users"])


def extract_tg_id(request: Request) -> int | None:
    if tg := request.headers.get("X-Telegram-Id"):
        return int(tg)
    if tg := request.cookies.get("tg_id"):
        return int(tg)
    if tg := request.query_params.get("tg_id"):
        return int(tg)
    return None


@router.get("/me", response_model=UserSchema, summary="Who am I?")
async def me(request: Request, db: AsyncSession = Depends(get_db)):
    tg_id = extract_tg_id(request)
    if tg_id is None:
        raise HTTPException(401, "telegram_id not provided")

    user = await user_crud.get_by_telegram_id(db, tg_id)

    # ─── если юзера нет, создаём ───────────────────────────────────
    if user is None:
        user = await user_crud.create(
            db,
            UserCreate(telegram_id=tg_id, username=f"user_{tg_id}"),
            extra_fields={"is_admin": tg_id in settings.admin_ids},
        )
    # ─── если есть, но флаг is_admin поменялся ─────────────────────
    elif user.is_admin != (tg_id in settings.admin_ids):
        user = await user_crud.update(
            db, user, {"is_admin": tg_id in settings.admin_ids}
        )

    return user
