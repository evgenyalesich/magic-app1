# backend/api/endpoints/admin_messages.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.api.deps import get_db, get_current_user
from backend.models.message import Message
from backend.models.user import User
from backend.schemas.message import MessageSchema, MessageReply

router = APIRouter(
    prefix="/admin/messages",
    tags=["Admin Messages"],
)


def ensure_admin(user: User):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только админ может сюда заходить",
        )
    return user


class MessageCreate(BaseModel):
    content: str


@router.get(
    "/",
    response_model=List[MessageSchema],
    summary="Админ: получить все сообщения (flat list)",
)
async def admin_list_all_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user, use_cache=False),
):
    ensure_admin(current_user)
    result = await db.execute(select(Message).order_by(Message.created_at))
    return result.scalars().all()


@router.get(
    "/{order_id}",
    response_model=List[MessageSchema],
    summary="Админ: история переписки по заказу",
)
async def admin_get_chat_by_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user, use_cache=False),
):
    ensure_admin(current_user)
    stmt = select(Message).where(Message.order_id == order_id).order_by(Message.created_at)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/{order_id}",
    response_model=MessageSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Админ: отправить сообщение в чат заказа",
)
async def admin_send_message(
    order_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user, use_cache=False),
):
    ensure_admin(current_user)
    msg = Message(
        user_id=current_user.id,
        order_id=order_id,
        content=payload.content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.post(
    "/{message_id}/reply",
    response_model=MessageSchema,
    summary="Админ: ответить на сообщение",
)
async def admin_reply_message(
    message_id: int,
    reply_in: MessageReply,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user, use_cache=False),
):
    ensure_admin(current_user)

    result = await db.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено",
        )

    msg.reply = reply_in.reply
    msg.replied_at = datetime.utcnow()
    await db.commit()
    await db.refresh(msg)
    return msg


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Админ: удалить сообщение",
)
async def admin_delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user, use_cache=False),
):
    ensure_admin(current_user)

    result = await db.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено",
        )

    await db.delete(msg)
    await db.commit()
    return
