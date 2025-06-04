from pydantic import BaseModel
from datetime import datetime


class MessageCreate(BaseModel):
    user_id: int
    order_id: int | None = None
    content: str


class MessageReply(BaseModel):
    reply: str


class MessageSchema(BaseModel):
    id: int
    user_id: int
    order_id: int | None
    content: str
    reply: str | None
    created_at: datetime
    replied_at: datetime | None

    class Config:
        from_attributes = True
