# backend/schemas/message.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# --------------------------------------------------------------------------
# общая конфигурация для всех схем: читаем поля напрямую из SQLAlchemy-ORM
# --------------------------------------------------------------------------
ORM_CONFIG = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# 1) сообщение, которое создаёт пользователь      (POST /messages/{id})
#    order_id берётся из URL-path,   is_read = False проставляется в сервисе
# --------------------------------------------------------------------------
class MessageCreate(BaseModel):
    content: str
    model_config = ORM_CONFIG


# --------------------------------------------------------------------------
# 2) ответ администратора в чат                    (POST /admin/messages/{id})
# --------------------------------------------------------------------------
class MessageReply(BaseModel):
    reply: str
    model_config = ORM_CONFIG


# --------------------------------------------------------------------------
# 3) то, что мы отдаём фронту (и пользователю, и админу)
#    ➜ добавили product_title, приходит через JOIN orders→products
#    ➜ добавили user_name, приходит через JOIN messages→users
# --------------------------------------------------------------------------
class MessageOut(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int] = None

    content: str
    reply: Optional[str] = None

    is_read: bool
    created_at: datetime
    replied_at: Optional[datetime] = None

    # название товара (из связки orders→products)
    product_title: Optional[str] = None
    # имя пользователя (username), от которого пришло сообщение
    user_name: Optional[str] = None

    model_config = ORM_CONFIG
