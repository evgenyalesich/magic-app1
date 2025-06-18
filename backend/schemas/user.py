# backend/schemas/user.py
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    telegram_id: int
    username: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: int
    telegram_id: int
    username: str
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)
