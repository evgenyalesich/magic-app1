from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from datetime import datetime


# ---------------------------------------------------------------------
# Базовые поля, которые повторяются в разных схемах
# ---------------------------------------------------------------------
class OrderBase(BaseModel):
    product_id: int
    quantity: int
    price: float


# ---------------------------------------------------------------------
# Входящая при создании (POST /orders/)
# ---------------------------------------------------------------------
class OrderCreate(OrderBase):
    user_id: int  # приходит от Telegram-Web-App


# ---------------------------------------------------------------------
# Ответ API (GET /orders/, POST /orders/, …)
# ---------------------------------------------------------------------
class OrderRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    price: Decimal
    total: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
