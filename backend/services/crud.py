# backend/services/crud.py
from __future__ import annotations

from typing import Any, Generic, Mapping, Optional, Type, TypeVar, Union, List, Dict
from uuid import UUID
from datetime import datetime, timezone

from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy import insert
from sqlalchemy.orm import joinedload

# ваши модели
from backend.models.category     import Category
from backend.models.message      import Message
from backend.models.order        import Order
from backend.models.order_item   import OrderItem
from backend.models.product      import Product
from backend.models.user         import User

# схема для админских сообщений
from backend.schemas.admin       import AdminMessageWithExtras

ModelT         = TypeVar("ModelT")
CreateSchemaT  = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT  = TypeVar("UpdateSchemaT", bound=BaseModel | Mapping[str, Any])

def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Преобразует спец-типы Pydantic в примитивы для БД."""
    for k, v in list(data.items()):
        if isinstance(v, HttpUrl):
            data[k] = str(v)
        elif isinstance(v, UUID):
            data[k] = str(v)
        elif isinstance(v, datetime):
            if v.tzinfo is not None:
                data[k] = v.astimezone(timezone.utc).replace(tzinfo=None)
    return data

class CRUDBase(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """Универсальный CRUD-помощник для SQLAlchemy моделей."""
    def __init__(self, model: Type[ModelT]) -> None:
        self.model = model

    # ---------- read ----------
    async def get(self, db: AsyncSession, id: int) -> Optional[ModelT]:
        return await db.get(self.model, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelT]:
        res = await db.execute(select(self.model).offset(skip).limit(limit))
        return res.scalars().all()

    async def get_all(self, db: AsyncSession) -> List[ModelT]:
        res = await db.execute(select(self.model))
        return res.scalars().all()

    async def get_by_telegram_id(self, db: AsyncSession, telegram_id: int) -> Optional[ModelT]:
        """Найти запись User по telegram_id."""
        if not hasattr(self.model, "telegram_id"):
            raise AttributeError(f"{self.model.__name__} has no attribute 'telegram_id'")
        res = await db.execute(
            select(self.model).where(self.model.telegram_id == telegram_id)
        )
        return res.scalars().first()

    async def get_or_create(
        self,
        db: AsyncSession,
        defaults: Optional[Mapping[str, Any]] = None,
        **unique_fields: Any,
    ) -> ModelT:
        """
        Найти объект по уникальным полям, или создать новый с defaults.
        """
        stmt = select(self.model).filter_by(**unique_fields).limit(1)
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            if defaults:
                for k, v in defaults.items():
                    setattr(existing, k, v)
                db.add(existing)
                await db.commit()
                await db.refresh(existing)
            return existing

        data = {**unique_fields, **(defaults or {})}
        return await self.create(db, data)

    # ---------- create ----------
    async def create(
        self,
        db: AsyncSession,
        obj_in: Union[CreateSchemaT, Mapping[str, Any]],
        extra_fields: Optional[Mapping[str, Any]] = None,
    ) -> ModelT:
        data = (
            obj_in.model_dump(mode="python", by_alias=True)
            if isinstance(obj_in, BaseModel)
            else dict(obj_in)
        )
        if extra_fields:
            data.update(extra_fields)
        db_obj = self.model(**_normalize(data))  # type: ignore[arg-type]
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # ---------- update ----------
    async def update(
        self,
        db: AsyncSession,
        obj_or_id: Union[int, ModelT],
        obj_in: UpdateSchemaT,
    ) -> ModelT:
        if isinstance(obj_or_id, int):
            db_obj = await self.get(db, obj_or_id)
            if db_obj is None:
                raise ValueError(f"{self.model.__name__} id={obj_or_id} not found")
        else:
            db_obj = obj_or_id

        update_data = (
            obj_in.model_dump(mode="python", exclude_unset=True, by_alias=True)
            if isinstance(obj_in, BaseModel)
            else dict(obj_in)
        )
        update_data = _normalize(update_data)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # ---------- delete ----------
    async def remove(
        self, db: AsyncSession, obj_or_id: Union[int, ModelT]
    ) -> ModelT:
        if isinstance(obj_or_id, int):
            db_obj = await self.get(db, obj_or_id)
            if db_obj is None:
                raise ValueError(f"{self.model.__name__} id={obj_or_id} not found")
        else:
            db_obj = obj_or_id

        await db.delete(db_obj)
        await db.commit()
        return db_obj

# Инстансы CRUD для каждой модели
user_crud       = CRUDBase[User,      BaseModel, BaseModel](User)
category_crud   = CRUDBase[Category,  BaseModel, BaseModel](Category)
product_crud    = CRUDBase[Product,   BaseModel, BaseModel](Product)
order_crud      = CRUDBase[Order,     BaseModel, BaseModel](Order)
order_item_crud = CRUDBase[OrderItem, BaseModel, BaseModel](OrderItem)
message_crud    = CRUDBase[Message,   BaseModel, BaseModel](Message)


# ──────────────────────────────────────────────────────────
# Специализированный CRUD для сообщений (админская часть)
# ──────────────────────────────────────────────────────────

class MessageCRUD:
    """Дополнительные методы по работе с Message."""
    async def create(self, db: AsyncSession, *, obj_in: BaseModel) -> Message:
        stmt = insert(Message).values(**obj_in.model_dump()).returning(Message)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()

    async def get_multi_by_order(self, db: AsyncSession, order_id: int) -> List[Message]:
        stmt = select(Message).where(Message.order_id == order_id).order_by(Message.created_at)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_admin_messages(self, db: AsyncSession) -> List[AdminMessageWithExtras]:
        """Возвращает список всех сообщений с доп. полями для админа."""
        stmt = (
            select(Message)
            .options(
                joinedload(Message.user),
                joinedload(Message.order).joinedload(Order.product)
            )
            .order_by(Message.created_at)
        )
        res = await db.execute(stmt)
        all_msgs: list[Message] = res.scalars().all()

        return [
            AdminMessageWithExtras(
                id=m.id,
                order_id=m.order_id,
                content=m.content,
                reply=m.reply,
                is_read=m.is_read,
                created_at=m.created_at,
                replied_at=m.replied_at,
                user_name=m.user.username,
                product_title=m.order.product.title,
            )
            for m in all_msgs
        ]


# Инстантируем
message_extra_crud = MessageCRUD()


# ──────────────────────────────────────────────────────────
# Админ-статистика
# ──────────────────────────────────────────────────────────

async def _scalar(db: AsyncSession, stmt):
    res = await db.execute(stmt)
    return res.scalar_one()

async def count_users(db: AsyncSession) -> int:
    return await _scalar(db, select(func.count()).select_from(User))

async def count_orders(db: AsyncSession) -> int:
    return await _scalar(db, select(func.count()).select_from(Order))

async def calculate_total_revenue(db: AsyncSession) -> float:
    val = await _scalar(db, select(func.sum(OrderItem.price)).select_from(OrderItem))
    return float(val or 0.0)

async def count_unread_messages(db: AsyncSession) -> int:
    if hasattr(Message, "is_read"):
        stmt = select(func.count()).select_from(Message).where(Message.is_read.is_(False))
    else:
        stmt = select(func.count()).select_from(Message).where(Message.replied_at.is_(None))
    return await _scalar(db, stmt)

class CRUDAdmin:
    async def get_admin_stats(self, db: AsyncSession) -> Dict[str, Any]:
        return {
            "total_users":     await count_users(db),
            "total_orders":    await count_orders(db),
            "total_revenue":   await calculate_total_revenue(db),
            "unread_messages": await count_unread_messages(db),
        }

admin_crud = CRUDAdmin()
