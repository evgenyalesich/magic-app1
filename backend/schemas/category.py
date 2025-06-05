# backend/schemas/category.py

from pydantic import BaseModel


class CategoryBase(BaseModel):
    """
    Базовая схема для категории:
      - name: str
    """

    name: str


class CategoryCreate(CategoryBase):
    """
    Схема для создания новой категории.
    Наследует поле `name` из CategoryBase.
    """

    pass


class CategoryRead(CategoryBase):
    """
    Схема для отдачи существующей категории из БД.
    Добавляет автоматически генерируемое поле `id: int`.
    """

    id: int

    class Config:
        orm_mode = True
