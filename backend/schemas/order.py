# backend/schemas/order.py

from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True

    # если всё-таки в бизнес-логике вам нужен список,
    # можно внутри __init__ сконструировать items:
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data["items"] = [
            {
                "product_id": data.pop("product_id"),
                "quantity": data.pop("quantity"),
                "price": data.pop("price"),
            }
        ]
        return data
