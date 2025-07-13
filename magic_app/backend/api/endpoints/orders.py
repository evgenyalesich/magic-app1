# backend/api/endpoints/orders.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select as future_select
from sqlalchemy.orm import joinedload

from backend.api.deps import get_db, get_current_user
from backend.models.order import Order
from backend.models.message import Message
from backend.models.user import User
from backend.schemas.order import OrderCreate, OrderRead, OrderDetail

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый заказ и сразу отправить приветственное сообщение",
)
async def create_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1) создаём сам заказ
    order = Order(user_id=current_user.id, **payload.dict())
    db.add(order)
    await db.commit()
    await db.refresh(order)

    # 2) выбираем администратора как отправителя (fallback — current_user)
    admin = (
        await db.execute(
            select(User).where(User.is_admin == True).limit(1)
        )
    ).scalar_one_or_none()
    sender_id = admin.id if admin else current_user.id

    # 3) автоматически создаём «приветственное» сообщение от админа
    welcome = Message(
        user_id=sender_id,
        order_id=order.id,
        content=(
            "Добрый день! Чтобы получить ваш расклад, "
            "пожалуйста, пришлите ваше имя, дату рождения и ваш вопрос."
        ),
    )
    db.add(welcome)
    await db.commit()
    await db.refresh(welcome)

    return order


@router.get(
    "/",
    response_model=list[OrderRead],
    summary="Список заказов текущего пользователя",
)
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        future_select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/my",
    response_model=list[OrderDetail],
    summary="История покупок текущего пользователя",
)
async def my_orders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        future_select(Order)
        .options(joinedload(Order.product))
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/{order_id}",
    response_model=OrderDetail,
    summary="Детали одного заказа",
)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        future_select(Order)
        .options(joinedload(Order.product))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )
    return order
