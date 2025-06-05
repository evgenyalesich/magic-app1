# backend/schemas/order.py

from datetime import datetime
from pydantic import BaseModel


class OrderBase(BaseModel):
    user_id: int


class OrderCreate(OrderBase):
    # ← instead of requiring `items: List[...]`, tests do:
    # OrderCreate(user_id=…, product_id=…, quantity=…, price=…)
    product_id: int
    quantity: int
    price: float


class OrderUpdate(BaseModel):
    quantity: int
    price: float


class OrderInDBBase(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Order(OrderInDBBase):
    pass
