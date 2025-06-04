import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session
from backend.services.crud import user_crud
from backend.schemas.user import UserCreate, UserSchema

router = APIRouter()
logger = logging.getLogger(__name__)

ADMIN_TELEGRAM_ID = 11111111


@router.post("/login", response_model=UserSchema)
async def login(user: UserCreate, db: AsyncSession = Depends(db_session)):

    logger.info(f"🔑 Логин пользователя: {user.telegram_id} ({user.username})")

    if user.telegram_id is None:
        raise HTTPException(status_code=400, detail="Telegram ID обязателен")

    # Ищем в БД
    existing_user = await user_crud.get_by_telegram_id(db, telegram_id=user.telegram_id)

    if not existing_user:
        # Если нет — создаём
        is_admin = user.telegram_id == ADMIN_TELEGRAM_ID
        user_in_db = await user_crud.create(
            db, obj_in=user, extra_fields={"is_admin": is_admin}
        )
        logger.info(f"✅ Пользователь {user_in_db.username} зарегистрирован в БД.")
    else:
        user_in_db = existing_user
        logger.info(f"🔄 Пользователь {user_in_db.username} уже существует в БД.")

    return user_in_db


@router.get("/user/{telegram_id}", response_model=UserSchema)
async def get_user(telegram_id: int, db: AsyncSession = Depends(db_session)):

    logger.info(f"📌 Запрос пользователя с Telegram ID: {telegram_id}")

    user = await user_crud.get_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        logger.warning(f"❌ Пользователь с Telegram ID {telegram_id} не найден")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    logger.info(f"✅ Найден пользователь: {user.username}")
    return user


async def get_current_user(
    telegram_id: int = Query(
        ..., alias="telegram_id", description="Telegram ID текущего пользователя"
    ),
    db: AsyncSession = Depends(db_session),
) -> UserSchema:

    user = await user_crud.get_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")
    return user
