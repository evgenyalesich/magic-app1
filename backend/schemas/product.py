# schemas/product.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    PositiveFloat,
)

# ─────────────────────────────────────────────
# 1.  Общее ядро полей
# ─────────────────────────────────────────────
class _ProductCore(BaseModel):
    """Поля, общие для всех схем (кроме id/created_at)."""
    title: str = Field(..., min_length=2, max_length=120, description="Название")
    description: Optional[str] = Field(None, max_length=2_000, description="Описание")
    image_url: Optional[HttpUrl] = Field(
        None,
        description="URL изображения",
        examples=["https://cdn.example.com/images/abc.jpg"],
    )
    price: PositiveFloat = Field(..., le=1_000_000, description="Цена, ₽")

    model_config = ConfigDict(str_strip_whitespace=True)


# ─────────────────────────────────────────────
# 2.  Создание
# ─────────────────────────────────────────────
class ProductCreate(_ProductCore):
    """
    Схема для POST /products.
    `category_id` можно не передавать — если его нет, приложение выберет
    подходящую категорию автоматически.
    """
    category_id: Optional[int] = Field(
        None, ge=1, description="ID категории (опционально)"
    )


# ─────────────────────────────────────────────
# 3.  Частичное обновление
# ─────────────────────────────────────────────
class ProductUpdate(BaseModel):
    """PATCH/PUT: можно менять любую комбинацию полей."""
    category_id: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, min_length=2, max_length=120)
    description: Optional[str] = Field(None, max_length=2_000)
    image_url: Optional[HttpUrl] = None
    price: Optional[PositiveFloat] = Field(None, le=1_000_000)

    model_config = ConfigDict(str_strip_whitespace=True)


# ─────────────────────────────────────────────
# 4.  То, что отдаём наружу
# ─────────────────────────────────────────────
class ProductOut(_ProductCore):
    """Схема, возвращаемая во всех GET-ответах."""
    id: int
    category_id: int = Field(..., ge=1, description="ID категории")
    created_at: datetime = Field(description="Дата создания (UTC)")

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# 5.  Back-compat alias (если где-то ожидают ProductSchema)
# ─────────────────────────────────────────────
ProductSchema = ProductOut  # noqa: N816
