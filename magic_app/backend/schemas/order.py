# backend/schemas/order.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from backend.schemas.product import ProductSchema            # «полный» товар
from backend.schemas.message import MessageOut            # сообщения

# общая конфигурация: позволяем Pydantic читать поля прямо из ORM-моделей
ORM_CONFIG = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
#          БАЗОВЫЕ СХЕМЫ (были)
# ---------------------------------------------------------------------------
class OrderBase(BaseModel):
    product_id: int
    quantity: int
    price: Decimal
    stars: Decimal = Decimal("0")

    model_config = ORM_CONFIG


class OrderCreate(OrderBase):
    user_id: int
    model_config = ORM_CONFIG


class OrderRead(OrderBase):
    id: int
    user_id: int
    total: Decimal
    status: str
    created_at: datetime

    # Полный объект товара
    product: ProductSchema

    model_config = ORM_CONFIG


class OrderDetail(OrderRead):
    # То же, но плюс вся переписка
    messages: list[MessageOut] = []
    model_config = ORM_CONFIG


# ---------------------------------------------------------------------------
#          ***   НОВОЕ   ***   История покупок пользователя
# ---------------------------------------------------------------------------
class _ProductLite(BaseModel):
    """
    Упрощённое представление товара для истории покупок.
    Содержит только то, что нужно показать в списке: название и картинку.
    """
    title: str
    image_url: str | None = None

    model_config = ORM_CONFIG


class OrderHistoryOut(BaseModel):
    """
    Схема для энд-пойнта `/orders/my` (история покупок).
    """
    id: int                          # ID заказа
    total: Decimal                   # Итоговая стоимость (руб.)
    paid_at: datetime | None         # Время оплаты (может быть None)
    product: _ProductLite            # Вложенный «облегчённый» товар

    model_config = ORM_CONFIG
