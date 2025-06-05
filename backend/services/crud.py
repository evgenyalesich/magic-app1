from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.sql import func

from backend.models import (
    User,
    Category,
    Product,
    Order,
    OrderItem,
    Message,
)
from backend.schemas.order import OrderCreate

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, SchemaType]):
    """Generic CRUD helper for SQLAlchemy models."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # ------------------------------------------------------------------
    # Basic CRUD
    # ------------------------------------------------------------------

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:  # noqa: A002
        """Возвращает объект по первичному ключу или *None*."""
        return await db.get(self.model, id)

    async def get_all(self, db: AsyncSession):
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: OrderCreate) -> Order:
        # 1) Создаём Order
        db_order = Order(user_id=obj_in.user_id)
        db.add(db_order)
        await db.flush()  # чтобы получить db_order.id

        # 2) Для каждого элемента из obj_in.items создаём OrderItem
        for item in obj_in.items:
            db_item = OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            db.add(db_item)

        await db.commit()
        await db.refresh(db_order)
        return db_order

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
        raise AttributeError(
            f"Model {self.model.__name__} does not have a 'telegram_id' attribute"
        )


user_crud = CRUDBase(User)
category_crud = CRUDBase(Category)
product_crud = CRUDBase(Product)
order_crud = CRUDBase(Order)
order_item_crud = CRUDBase(OrderItem)
message_crud = CRUDBase(Message)


async def count_users(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def count_orders(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Order))
    return result.scalar_one()


async def calculate_total_revenue(db: AsyncSession) -> float:
    result = await db.execute(select(func.sum(OrderItem.price)).select_from(OrderItem))
    return float(result.scalar_one() or 0.0)


async def count_unread_messages(db: AsyncSession) -> int:
    """Поддержка разных схем: is_read или replied_at."""
    if hasattr(Message, "is_read"):
        stmt = (
            select(func.count()).select_from(Message).where(Message.is_read.is_(False))
        )
    else:
        stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.replied_at.is_(None))
        )
    result = await db.execute(stmt)
    return result.scalar_one()


class CRUDAdmin:
    async def get_admin_stats(self, db: AsyncSession) -> dict:
        """Собирает показатели для административной панели."""
        total_users = await count_users(db)
        total_orders = await count_orders(db)
        total_revenue = await calculate_total_revenue(db)
        unread_messages = await count_unread_messages(db)

        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "unread_messages": unread_messages,
        }


admin_crud = CRUDAdmin()
