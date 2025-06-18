# backend/schemas/message.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# единая конфигурация «чтение из ORM»
ORM_CONFIG = ConfigDict(from_attributes=True)


# ────────────────────────────────────────────────────────────
# DTO: входящее сообщение от пользователя
# ────────────────────────────────────────────────────────────
class MessageCreate(BaseModel):
    user_id: int
    content: str
    is_read: bool = False           # по умолчанию ещё не прочитано

    model_config = ORM_CONFIG


# ────────────────────────────────────────────────────────────
# DTO: ответ администратора
# ────────────────────────────────────────────────────────────
class MessageReply(BaseModel):
    reply: str

    model_config = ORM_CONFIG


# ────────────────────────────────────────────────────────────
# DTO: полная структура сообщения,
#       которую возвращает API
# ────────────────────────────────────────────────────────────
class MessageSchema(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int] = None      # связь с заказом (если есть)
    content: str
    reply: Optional[str] = None
    is_read: bool
    created_at: datetime
    replied_at: Optional[datetime] = None

    model_config = ORM_CONFIG
