# backend/models/product.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)  # <-- Float вместо Numeric
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String, index=True)
    image_url = Column(String, nullable=True)
    category = relationship("Category", back_populates="products")
    description = Column(Text, nullable=True)  # ← добавили поле description
