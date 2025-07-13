from __future__ import annotations

"""SQLAlchemy + Pydantic user models (без постоянного хранения tg‑hash).

* Поле `tg_hash` удалено из таблицы и DTO: мы больше не кэшируем подпись.
* Остался только `telegram_id` как уникальный ключ для поиска пользователя.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.models.base import Base

# -------------------------------------------------------------
# SQLAlchemy User model (БД)
# -------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)

    # NOTE: tg_hash удалён → столбца больше нет.
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    stars = Column(Integer, default=0, nullable=False)
    total_orders = Column(Integer, default=0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)

    first_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Связь с заказами
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


# -------------------------------------------------------------
# Pydantic‑схемы пользователя (DTO)
# -------------------------------------------------------------
ORM_CONFIG = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Базовые поля профиля, которые могут приходить с фронта."""

    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: Optional[str] = Field(None, description="Username в Telegram")

    model_config = ORM_CONFIG


class UserCreate(UserBase):
    """Схема создания нового пользователя."""

    model_config = ORM_CONFIG


class UserUpdate(BaseModel):
    """Разрешённые изменения профиля через API."""

    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    stars: Optional[int] = None

    model_config = ORM_CONFIG


class UserSchema(UserBase):
    """Что отдаём клиенту."""

    id: int
    is_active: bool
    is_admin: bool
    stars: int
    total_orders: int
    total_spent: float
    first_seen: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ORM_CONFIG


class UserInDB(UserSchema):
    """Расширенная схема для внутреннего кода (если нужно)."""

    model_config = ORM_CONFIG
