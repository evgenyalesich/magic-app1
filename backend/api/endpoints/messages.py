from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.core.database import get_db
from backend.models.order import Order
from backend.models.message import Message
from backend.schemas.message import MessageCreate, MessageSchema

router = APIRouter()


@router.post("/", response_model=MessageSchema)
async def create_message(message_in: MessageCreate, db: AsyncSession = Depends(get_db)):
    # Проверка существования заказа по order_id
    stmt = select(Order).where(Order.id == message_in.order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден.")



    new_message = Message(**message_in.dict())

    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message
