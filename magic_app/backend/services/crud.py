from __future__ import annotations

"""Shared CRUD helpers и конкретные инстансы.

Изменения:
1. `UserCRUD.get_or_create_user` больше **не принимает first_name / last_name**
   (эти колонки удалены из модели).
2. Метод фильтрует `defaults`, чтобы никогда не писать в несуществующие поля.
3. Общий `get_or_create` уже защищён от гонки вставки и лишних UPDATE.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Mapping, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, HttpUrl
from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

# ─────────────────────── SQL-Alchemy модели ────────────────────────────
from backend.models.category import Category
from backend.models.message import Message
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.product import Product
from backend.models.user import User

# Pydantic-схема, в которую «разворачиваем» админ-сообщения
from backend.schemas.admin import AdminMessageWithExtras

ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel | Mapping[str, Any])

# ───────────────────────── utils ────────────────────────────────────────
def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Преобразует спец-типы Pydantic к примитивам SQL."""
    for k, v in list(data.items()):
        if isinstance(v, (HttpUrl, UUID)):
            data[k] = str(v)
        elif isinstance(v, datetime) and v.tzinfo:
            data[k] = v.astimezone(timezone.utc).replace(tzinfo=None)
    return data


# ───────────────────────── базовый CRUD ─────────────────────────────────
class CRUDBase(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    def __init__(self, model: Type[ModelT]) -> None:
        self.model = model

    # ---------- READ ----------
    async def get(self, db: AsyncSession, id: int) -> Optional[ModelT]:
        return await db.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelT]:
        res = await db.execute(select(self.model).offset(skip).limit(limit))
        return res.scalars().all()

    async def get_all(self, db: AsyncSession) -> List[ModelT]:
        res = await db.execute(select(self.model))
        return res.scalars().all()

    async def get_by_telegram_id(self, db: AsyncSession, telegram_id: int) -> Optional[ModelT]:
        if not hasattr(self.model, "telegram_id"):
            raise AttributeError(f"{self.model.__name__} has no attribute 'telegram_id'")
        stmt = select(self.model).where(self.model.telegram_id == telegram_id)
        return (await db.execute(stmt)).scalars().first()

    async def get_or_create(
        self,
        db: AsyncSession,
        defaults: Optional[Mapping[str, Any]] = None,
        **unique_fields: Any,
    ) -> ModelT:
        # 1. Пытаемся найти существующего
        stmt = select(self.model).filter_by(**unique_fields).limit(1)
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            if defaults:  # ленивый UPDATE
                changed = False
                for k, v in defaults.items():
                    if getattr(existing, k, None) != v:
                        setattr(existing, k, v)
                        changed = True
                if changed:
                    db.add(existing)
                    await db.commit()
                    await db.refresh(existing)
            return existing

        # 2. Пытаемся создать
        data = {**unique_fields, **(defaults or {})}
        try:
            return await self.create(db, data)
        except IntegrityError:
            # Гонка: параллельный запрос успел вставить
            await db.rollback()
            return (await db.execute(stmt)).scalars().one()

    # ---------- CREATE ----------
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

    # ---------- UPDATE ----------
    async def update(
        self, db: AsyncSession, obj_or_id: Union[int, ModelT], obj_in: UpdateSchemaT
    ) -> ModelT:
        db_obj = await self.get(db, obj_or_id) if isinstance(obj_or_id, int) else obj_or_id
        if db_obj is None:
            raise ValueError(f"{self.model.__name__} not found")

        update_data = (
            obj_in.model_dump(mode="python", exclude_unset=True, by_alias=True)
            if isinstance(obj_in, BaseModel)
            else dict(obj_in)
        )
        for field, value in _normalize(update_data).items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # ---------- DELETE ----------
    async def remove(self, db: AsyncSession, obj_or_id: Union[int, ModelT]) -> ModelT:
        db_obj = await self.get(db, obj_or_id) if isinstance(obj_or_id, int) else obj_or_id
        if db_obj is None:
            raise ValueError(f"{self.model.__name__} not found")

        await db.delete(db_obj)
        await db.commit()
        return db_obj


# ─────────────────────── User-specific CRUD ────────────────────────────
class UserCRUD(CRUDBase[User, BaseModel, BaseModel]):
    """Расширяет базовый CRUD удобным upsert-методом."""

    async def get_or_create_user(
        self,
        db: AsyncSession,
        *,
        telegram_id: int,
        username: str = "",
        **kwargs  # Принимаем дополнительные параметры, но фильтруем их
    ) -> User:
        """
        Создает или получает пользователя по telegram_id.

        ВАЖНО: Метод автоматически отфильтровывает параметры, которых нет в модели User.
        Это сделано для обратной совместимости с кодом, который может передавать
        first_name, last_name и другие удаленные поля.
        """
        # Получаем список всех колонок в таблице User
        allowed_columns = {c.name for c in self.model.__table__.columns}

        # Формируем defaults только из реально существующих колонок
        defaults = {"username": username}

        # Добавляем дополнительные параметры, если они есть в модели
        for key, value in kwargs.items():
            if key in allowed_columns:
                defaults[key] = value

        # Убираем из defaults поля, которых нет в модели
        defaults = {k: v for k, v in defaults.items() if k in allowed_columns}

        return await self.get_or_create(db, telegram_id=telegram_id, defaults=defaults)

    async def create_user(
        self,
        db: AsyncSession,
        *,
        telegram_id: int,
        username: str = "",
        **kwargs  # Принимаем дополнительные параметры, но фильтруем их
    ) -> User:
        """
        Создает нового пользователя с фильтрацией полей.
        """
        # Получаем список всех колонок в таблице User
        allowed_columns = {c.name for c in self.model.__table__.columns}

        # Формируем данные для создания
        data = {
            "telegram_id": telegram_id,
            "username": username
        }

        # Добавляем дополнительные параметры, если они есть в модели
        for key, value in kwargs.items():
            if key in allowed_columns:
                data[key] = value

        # Убираем из data поля, которых нет в модели
        data = {k: v for k, v in data.items() if k in allowed_columns}

        return await self.create(db, data)


# ────────────────────── instantiate CRUD-объектов ──────────────────────
user_crud       = UserCRUD(User)
category_crud   = CRUDBase[Category,  BaseModel, BaseModel](Category)
product_crud    = CRUDBase[Product,   BaseModel, BaseModel](Product)
order_crud      = CRUDBase[Order,     BaseModel, BaseModel](Order)
order_item_crud = CRUDBase[OrderItem, BaseModel, BaseModel](OrderItem)
message_crud    = CRUDBase[Message,   BaseModel, BaseModel](Message)

# ─────────────────────────── MessageCRUD ────────────────────────────────
class MessageCRUD:
    """Расширенный CRUD, содержащий всё, что нужно фронту."""

    # ---- создание сообщения (пользователь / админ) --------------------
    async def create(self, db: AsyncSession, *, obj_in: BaseModel) -> Message:
        stmt = insert(Message).values(**obj_in.model_dump()).returning(Message)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()

    # ---- сообщения конкретного заказа ---------------------------------
    async def get_multi_by_order(
        self, db: AsyncSession, order_id: int
    ) -> List[Message]:
        """
        JOIN-им product, чтобы сразу «пришилить» message.product_title
        (см. схемы — MessageOut.product_title).
        """
        stmt = (
            select(Message)
            .where(Message.order_id == order_id)
            .order_by(Message.created_at)
            .options(
                joinedload(Message.order).joinedload(Order.product)  # for product_title
            )
        )
        res = await db.execute(stmt)
        msgs: list[Message] = res.scalars().all()

        # вручную «пришиваем» product_title, чтобы Pydantic забрал его
        for m in msgs:
            if m.order and m.order.product:
                m.product_title = m.order.product.title  # type: ignore[attr-defined]
            else:
                m.product_title = None  # type: ignore[attr-defined]
        return msgs

    # ---- список чатов пользователя ------------------------------------
    async def get_user_chats(
        self, db: AsyncSession, user_id: int
    ) -> List[dict[str, Any]]:
        """
        Возвращает список: один элемент на заказ пользователя,
        c названием товара и последним сообщением.
        """
        # 1. все заказы конкретного пользователя + product
        orders_stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.product))
        )
        orders = (await db.execute(orders_stmt)).scalars().all()

        if not orders:
            return []

        order_ids = [o.id for o in orders]

        # 2. для каждой order_id найдём timestamp последнего сообщения
        last_ts_subq = (
            select(
                Message.order_id,
                func.max(Message.created_at).label("last_ts"),
            )
            .where(Message.order_id.in_(order_ids))
            .group_by(Message.order_id)
            .subquery()
        )

        # 3. подтягиваем сами «последние» сообщения
        last_msgs_stmt = (
            select(Message)
            .join(
                last_ts_subq,
                (Message.order_id == last_ts_subq.c.order_id)
                & (Message.created_at == last_ts_subq.c.last_ts),
            )
        )
        last_msgs = (await db.execute(last_msgs_stmt)).scalars().all()
        last_msg_map = {m.order_id: m for m in last_msgs}

        # 4. собираем финальную структуру
        result: list[dict[str, Any]] = []
        for ord_obj in orders:
            last_msg = last_msg_map.get(ord_obj.id)
            result.append(
                {
                    "order_id": ord_obj.id,
                    "product": {"title": ord_obj.product.title if ord_obj.product else None},
                    "last_message": {
                        "id": last_msg.id,
                        "content": last_msg.content,
                        "created_at": last_msg.created_at,
                        "is_admin": last_msg.is_admin,
                    }
                    if last_msg
                    else None,
                }
            )
        # сортируем по дате последнего сообщения (null - в конец)
        result.sort(
            key=lambda x: x["last_message"]["created_at"]
            if x["last_message"]
            else datetime.min,
            reverse=True,
        )
        return result

    # ---- админ видит ВСЕ сообщения со связями -------------------------
    async def get_admin_messages(self, db: AsyncSession) -> List[AdminMessageWithExtras]:
        stmt = (
            select(Message)
            .options(
                joinedload(Message.user),
                joinedload(Message.order).joinedload(Order.product),
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
                product_title=m.order.product.title if m.order and m.order.product else None,
            )
            for m in all_msgs
        ]


# инстанс расширенного CRUD
message_extra_crud = MessageCRUD()

# ────────────────────────── админ-метрики ───────────────────────────────
async def _scalar(db: AsyncSession, stmt):
    return (await db.execute(stmt)).scalar_one()

async def count_users(db: AsyncSession) -> int:
    return await _scalar(db, select(func.count()).select_from(User))

async def count_orders(db: AsyncSession) -> int:
    return await _scalar(db, select(func.count()).select_from(Order))

async def calculate_total_revenue(db: AsyncSession) -> float:
    val = await _scalar(db, select(func.sum(OrderItem.price)).select_from(OrderItem))
    return float(val or 0.0)

async def count_unread_messages(db: AsyncSession) -> int:
    column = Message.is_read if hasattr(Message, "is_read") else Message.replied_at
    stmt = select(func.count()).select_from(Message).where(column.is_(False))
    return await _scalar(db, stmt)


class CRUDAdmin:
    async def get_admin_stats(self, db: AsyncSession) -> Dict[str, Any]:
        return {
            "total_users": await count_users(db),
            "total_orders": await count_orders(db),
            "total_revenue": await calculate_total_revenue(db),
            "unread_messages": await count_unread_messages(db),
        }


admin_crud = CRUDAdmin()
