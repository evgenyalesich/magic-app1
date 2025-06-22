# backend/schemas/user.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: int
    username: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ─────────────────── CREATE / UPDATE ───────────────────
class UserCreate(UserBase):
    username: str                   # username обязателен при создании


class UserUpdate(BaseModel):
    """Частичное обновление профиля (patch)."""
    username: str | None = None
    is_admin: bool | None = None

    model_config = ConfigDict(from_attributes=True)


# ─────────────────── READ ───────────────────
class UserSchema(UserBase):
    id: int
    is_admin: bool
    first_seen: datetime | None = None
    total_orders: int | None = None
    total_spent: float | None = None

    model_config = ConfigDict(from_attributes=True)
