from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: int
    username: str | None = None


class UserCreate(UserBase):
    pass


class UserSchema(UserBase):
    id: int
    first_seen: datetime
    total_orders: int
    total_spent: float
    is_admin: bool  # <-- Добавляем обязательное поле!

    class Config:
        from_attributes = True
