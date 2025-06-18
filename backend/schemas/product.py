# backend/schemas/product.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    category_id: int
    title: str
    description: str | None = None
    image_url: str | None = None
    price: Decimal                       # точнее для денег, чем float

    # одна-единственная конфигурация v2
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(ProductBase):
    """DTO для создания товара ― те же поля, что и у ProductBase."""
    pass


class ProductSchema(ProductBase):
    """DTO для чтения товара из БД."""
    id: int
    created_at: datetime

    # оставляем возможность читать из ORM-объекта
    model_config = ConfigDict(from_attributes=True)
