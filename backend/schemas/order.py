# backend/schemas/order.py

from datetime import datetime
from pydantic import BaseModel


class OrderBase(BaseModel):
    user_id: int


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


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
