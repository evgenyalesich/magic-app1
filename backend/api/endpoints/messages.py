# backend/api/endpoints/messages.py
from typing                 import List
from fastapi                import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future      import select
from backend.api.deps        import get_db, get_current_user
from backend.models.order    import Order
from backend.models.message  import Message
from backend.models.user     import User
from backend.schemas.message import MessageCreate, MessageSchema

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)

async def check_order_and_rights(
    order_id: int,
    current_user: User,
    db: AsyncSession,
) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if not (current_user.is_admin or order.user_id == current_user.id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")
    return order

@router.get(
    "/",
    response_model=List[MessageSchema],
    summary="Список всех сообщений (чаты)",
)
async def fetch_user_chats(
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.is_admin:
        result = await db.execute(select(Message).order_by(Message.created_at))
    else:
        result = await db.execute(
            select(Message)
            .join(Order, Order.id == Message.order_id)
            .where(Order.user_id == current_user.id)
            .order_by(Message.created_at)
        )
    return result.scalars().all()

@router.get(
    "/{order_id}",
    response_model=List[MessageSchema],
    summary="История переписки по заказу",
)
async def list_messages(
    order_id: int,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_order_and_rights(order_id, current_user, db)
    result = await db.execute(
        select(Message)
        .where(Message.order_id == order_id)
        .order_by(Message.created_at)
    )
    return result.scalars().all()

@router.post(
    "/{order_id}",
    response_model=MessageSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить сообщение в чат заказа",
)
async def create_message(
    order_id: int,
    message_in: MessageCreate,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем права доступа к заказу
    await check_order_and_rights(order_id, current_user, db)

    # Создаем сообщение
    msg = Message(
        order_id=order_id,
        user_id=current_user.id,
        content=message_in.content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить своё сообщение",
)
async def delete_message(
    message_id: int,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    if not (current_user.is_admin or msg.user_id == current_user.id):
        raise HTTPException(status_code=403, detail="Нет прав удалять это сообщение")
    await db.delete(msg)
    await db.commit()
    return
