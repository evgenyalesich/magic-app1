# backend/schemas/message.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# единая конфигурация «чтение из ORM»
ORM_CONFIG = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    content: str
    # Убираем order_id и is_read, так как они берутся из URL и устанавливаются по умолчанию
    model_config = ORM_CONFIG

class MessageReply(BaseModel):
    reply: str                 # тело ответа от админа
    model_config = ORM_CONFIG

class MessageSchema(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int] = None
    content: str
    reply: Optional[str] = None
    is_read: bool
    created_at: datetime
    replied_at: Optional[datetime] = None
    model_config = ORM_CONFIG
