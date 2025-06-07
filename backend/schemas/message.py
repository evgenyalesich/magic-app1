from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    user_id: int
    content: str
    is_read: bool

    class Config:
        orm_mode = True


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
        orm_mode = True
