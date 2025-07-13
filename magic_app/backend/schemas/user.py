# backend/schemas/user.py
from pydantic import BaseModel, ConfigDict, Field
from typing    import Optional
from datetime  import datetime

# Общая конфигурация для всех ORM-схем
ORM_CONFIG = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    """
    Базовые поля профиля: Telegram ID и опциональный username.
    """
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username:    Optional[str] = Field(None, description="Username в Telegram")

    model_config = ORM_CONFIG


class UserCreate(UserBase):
    """
    Схема создания нового пользователя через Telegram.
    """
    # всё наследуется из UserBase — дополнительных полей не нужно
    model_config = ORM_CONFIG


class UserUpdate(BaseModel):
    """
    Частичное обновление профиля.
    Можно менять только username, статус активности, роли и счётчики.
    """
    username:    Optional[str]  = None
    is_active:   Optional[bool] = None
    is_admin:    Optional[bool] = None
    stars:       Optional[int]  = None

    model_config = ORM_CONFIG


class UserSchema(UserBase):
    """
    Схема отдачи профиля клиенту.
    """
    id:           int
    is_active:    bool
    is_admin:     bool
    stars:        int
    total_orders: int
    total_spent:  float
    first_seen:   Optional[datetime]
    created_at:   datetime
    updated_at:   Optional[datetime]

    model_config = ORM_CONFIG


class UserInDB(UserSchema):
    """
    Внутренняя схема для работы с БД.
    (Без поля пароля/хэша, т.к. регистрация только через Telegram.)
    """
    model_config = ORM_CONFIG
