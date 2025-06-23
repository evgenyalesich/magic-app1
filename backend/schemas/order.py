# backend/schemas/order.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

# Импортируем ProductOut под именем ProductSchema
from backend.schemas.product import ProductSchema
# Импортируем схему сообщения
from backend.schemas.message import MessageSchema

ORM_CONFIG = ConfigDict(from_attributes=True)

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

    # вот тут вложенный товар
    product: ProductSchema

    model_config = ORM_CONFIG

class OrderDetail(OrderRead):
    # и здесь — помимо product ещё и переписка
    messages: list[MessageSchema] = []

    model_config = ORM_CONFIG
