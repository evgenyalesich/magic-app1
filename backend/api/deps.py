# backend/api/deps.py

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.crud import user_crud
from backend.core.config import settings
from backend.core.database import get_db
from backend.schemas.user import UserSchema


async def get_current_user(
    tg_id_cookie: str = Depends(lambda request: request.cookies.get("tg_id")),
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """
    Берём tg_id из cookie, ищем в БД.
    """
    if not tg_id_cookie:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        tg_id_val = int(tg_id_cookie)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неправильный tg_id")
    user = await user_crud.get_by_telegram_id(db, telegram_id=tg_id_val)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


def admin_guard(current_user: UserSchema = Depends(get_current_user)):
    """
    Dependency-функция для админских роутов: если current_user.telegram_id
    не в списке админов → 403 Forbidden.
    """
    if current_user.telegram_id not in settings.ADMIN_TG_IDS:
        raise HTTPException(status_code=403, detail="Требуется права администратора")
    return current_user
