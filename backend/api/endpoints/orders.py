from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db  # ← правильный импорт
from backend.schemas.order import OrderCreate, OrderRead
from backend.services.crud import order_crud

router = APIRouter(
    prefix="/orders",  # ← убираем лишнее /api
    tags=["orders"],
)

# ---------- CRUD ----------


@router.get("/", response_model=List[OrderRead])
async def list_orders(db: AsyncSession = Depends(get_db)):
    """Список заказов."""
    return await order_crud.get_all(db)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await order_crud.get(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await order_crud.create(db, order_in)
