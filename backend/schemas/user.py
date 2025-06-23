# backend/schemas/user.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing    import Optional
from datetime  import datetime
import re

# Общая конфигурация для всех ORM-схем
ORM_CONFIG = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    """
    Базовые поля, общие и для e-mail регистрации, и для Telegram.
    """
    telegram_id: Optional[int] = None
    username:    Optional[str] = None
    email:       Optional[str] = None  # Changed from EmailStr to str

    # Custom email validation without email-validator dependency
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        # Simple regex pattern for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v

    model_config = ORM_CONFIG

class UserCreate(UserBase):
    """
    Схема создания нового пользователя.
    Для e-mail-регистрации обязательны email + password,
    для Telegram — telegram_id (username/email по желанию).
    """
    password: Optional[str] = None
    telegram_id: Optional[int] = Field(
        None,
        description="Telegram ID, если регистрация через бота"
    )
    model_config = ORM_CONFIG

class UserUpdate(BaseModel):
    """
    Частичное обновление профиля (PATCH).
    Можно менять любые поля кроме id.
    """
    username:    Optional[str] = None
    email:       Optional[str] = None  # Changed from EmailStr to str
    password:    Optional[str] = None
    is_active:   Optional[bool] = None
    is_admin:    Optional[bool] = None
    stars:       Optional[int] = None

    # Custom email validation for update as well
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v

    model_config = ORM_CONFIG

class UserSchema(UserBase):
    """
    Схема возвращаемого профиля пользователя.
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
    Схема, которая хранится в БД (добавляется хэш пароля).
    Не возвращается клиенту.
    """
    hashed_password: str
    model_config = ORM_CONFIG
