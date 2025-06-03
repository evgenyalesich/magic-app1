from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.sql import func

from backend.models import User, Category, Product, Order, OrderItem, Message

ModelType = TypeVar('ModelType')
SchemaType = TypeVar('SchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, SchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType:
        return await db.get(self.model, id)

    async def get_all(self, db: AsyncSession):
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: SchemaType, extra_fields: dict | None = None) -> ModelType:
        obj_data = obj_in.dict()
        if extra_fields:
            obj_data.update(extra_fields)
        obj = self.model(**obj_data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: dict):
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, db_obj: ModelType):
        await db.delete(db_obj)
        await db.commit()
        return db_obj

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_telegram_id(self, db: AsyncSession, telegram_id: str):
        if hasattr(self.model, "telegram_id"):
            result = await db.execute(
                select(self.model).where(self.model.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
        raise AttributeError(f"Model {self.model.__name__} does not have a 'telegram_id' attribute")


user_crud = CRUDBase(User)
category_crud = CRUDBase(Category)
product_crud = CRUDBase(Product)
order_crud = CRUDBase(Order)
order_item_crud = CRUDBase(OrderItem)
message_crud = CRUDBase(Message)


class CRUDAdmin:
    async def get_admin_stats(self, db: AsyncSession):
        """Получение статистики для админ-панели"""
        total_users = await db.execute(select(func.count()).select_from(User))
        total_orders = await db.execute(select(func.count()).select_from(Order))
        total_revenue = await db.execute(select(func.sum(OrderItem.price)).select_from(OrderItem))
        unread_messages = await db.execute(select(func.count()).select_from(Message).where(Message.is_read == False))

        return {
            "total_users": total_users.scalar_one(),
            "total_orders": total_orders.scalar_one(),
            "total_revenue": total_revenue.scalar_one() or 0.0,
            "unread_messages": unread_messages.scalar_one(),
        }


admin_crud = CRUDAdmin()
