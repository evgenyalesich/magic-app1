# backend/schemas/order.py
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# ──────────────────────────────────────────────────────────────────────
# Общая конфигурация для всех схем (чтение из ORM)
# ──────────────────────────────────────────────────────────────────────
ORM_CONFIG = ConfigDict(from_attributes=True)


# ──────────────────────────────────────────────────────────────────────
# Базовые поля заказа (используются в нескольких схемах)
# ──────────────────────────────────────────────────────────────────────
class OrderBase(BaseModel):
    product_id: int
    quantity: int
    price: Decimal                     # используем Decimal для денег

    model_config = ORM_CONFIG


# ──────────────────────────────────────────────────────────────────────
# DTO, приходящая при создании заказа (POST /orders/)
# ──────────────────────────────────────────────────────────────────────
class OrderCreate(OrderBase):
    user_id: int                       # приходит из Telegram Web-App


# ──────────────────────────────────────────────────────────────────────
# DTO, возвращаемая API (GET /orders/, POST /orders/, …)
# ──────────────────────────────────────────────────────────────────────
class OrderRead(OrderBase):
    id: int
    user_id: int
    total: Decimal
    created_at: datetime

    model_config = ORM_CONFIG
