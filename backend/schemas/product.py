from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    category_id: int
    title: str
    description: str | None = None
    image_url: str | None = None
    price: float

class ProductCreate(ProductBase):
    pass

class ProductSchema(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
