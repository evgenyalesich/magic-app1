# backend/schemas/category.py
from pydantic import BaseModel, ConfigDict


# одна общая конфигурация, разрешающая чтение из ORM-объектов
ORM_CONFIG = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    """
    Базовая схема категории (только имя).
    """
    name: str

    model_config = ORM_CONFIG


class CategoryCreate(CategoryBase):
    """
    Используется при создании новой категории.
    Наследует поле `name` без изменений.
    """
    # дополнительных полей нет
    pass


class CategoryRead(CategoryBase):
    """
    Схема, которую возвращает API для существующей категории.
    Добавляется авто-генерируемое поле `id`.
    """
    id: int

    model_config = ORM_CONFIG
