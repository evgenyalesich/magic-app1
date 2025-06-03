from pydantic import BaseModel
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItemCreate]

class OrderSchema(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
