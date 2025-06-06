# backend/api/endpoints/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db  # <-- ваша зависимость
from backend.schemas.order import OrderCreate, OrderRead
from backend.services.crud import order_crud

router = APIRouter(prefix="/orders", tags=["orders"])


# ---------- Существующий POST ----------
@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await order_crud.create(db, order_in)


# ---------- Новый список ----------
@router.get("/", response_model=list[OrderRead])
async def list_orders(db: AsyncSession = Depends(get_db)):
    orders = await order_crud.get_all(db)
    return [OrderRead.model_validate(o) for o in orders]


# ---------- Новый «детально» ----------
@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await order_crud.get(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
