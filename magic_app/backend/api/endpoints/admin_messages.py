# backend/api/endpoints/admin_messages.py
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import (
    get_db,
    admin_guard,
    get_current_user,
)

# нотификаторы (e-mail / бот), сам manager с WS не нужен
from backend.api.websockets.manager import (
    notify_new_message_to_admins as notify_admins,
    notify_admin_reply_to_user   as notify_user_about_reply,
)

from backend.models.message import Message
from backend.models.user    import User
from backend.schemas.message import MessageCreate, MessageOut, MessageReply

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin • Messages"])


# ---------------------------------------------------------------------------#
#                       вспомогательные утилиты                              #
# ---------------------------------------------------------------------------#
def _parse_since(raw: Optional[str]) -> Optional[datetime]:
    """ISO-строка → datetime | None"""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(422, "Параметр since/after должен быть ISO-датой")


async def push_to_order_subscribers(order_id: int, update_type: str, data: dict):
    """Заглушка: просто логируем событие, без WS-рассылки."""
    logger.info(
        f"[polling-mode] order={order_id} update={update_type} payload={data}"
    )


# ---------------------------------------------------------------------------#
#                              LONG-POLL                                     #
# ---------------------------------------------------------------------------#
LONGPOLL_TIMEOUT = 25        # секунд
CHECK_INTERVAL   = 1         # опрос БД

@router.get(
    "/{order_id}/poll",
    response_model=List[MessageOut],
    summary="Long-poll: новые сообщения после ?after",
    dependencies=[Depends(admin_guard)],
)
async def poll_chat_long(
    order_id: int,
    after: Optional[str] = Query(
        default=None, description="ISO-метка последнего сообщения"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Держит соединение ≤ 25 с. Если появились новые записи — сразу отдаёт их.
    Иначе по тайм-ауту возвращает [].
    """
    ts = _parse_since(after)
    deadline = datetime.utcnow() + timedelta(seconds=LONGPOLL_TIMEOUT)

    while datetime.utcnow() < deadline:
        stmt = (
            select(Message)
            .where(Message.order_id == order_id)
            .order_by(Message.created_at)
        )
        if ts:
            stmt = stmt.where(Message.created_at > ts)

        rows = (await db.execute(stmt)).scalars().all()
        if rows:
            return rows

        await asyncio.sleep(CHECK_INTERVAL)

    return []


# ---------------------------------------------------------------------------#
#                        история / инкрементальное                           #
# ---------------------------------------------------------------------------#
@router.get(
    "/{order_id}",
    response_model=List[MessageOut],
    summary="История чата (или новые после ?since)",
    dependencies=[Depends(admin_guard)],
)
async def list_chat(
    order_id: int,
    since: Optional[str] = Query(
        default=None, description="ISO-дата: вернуть записи НОВЕЕ неё"
    ),
    db: AsyncSession = Depends(get_db),
):
    ts = _parse_since(since)
    stmt = (
        select(Message)
        .where(Message.order_id == order_id)
        .order_by(Message.created_at)
    )
    if ts:
        stmt = stmt.where(Message.created_at > ts)
    return (await db.execute(stmt)).scalars().all()


# ---------------------------------------------------------------------------#
#                           отправить сообщение                               #
# ---------------------------------------------------------------------------#
@router.post(
    "/{order_id}",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Админ: отправить сообщение",
    dependencies=[Depends(admin_guard)],
)
async def admin_send_message(
    order_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_user),
):
    try:
        msg = Message(
            user_id=admin.id,
            order_id=order_id,
            content=payload.content,
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)

        await push_to_order_subscribers(
            order_id,
            "new_message",
            {"message": {
                "id": msg.id,
                "user_id": msg.user_id,
                "order_id": msg.order_id,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "is_admin": True,
            }},
        )

        await notify_admins(msg, admin.id)
        logger.info(f"✅ Админ {admin.id} отправил сообщение в заказ {order_id}")
        return msg

    except Exception as e:
        logger.error(f"❌ admin_send_message: {e}")
        await db.rollback()
        raise HTTPException(500, "Не удалось отправить сообщение")


# ---------------------------------------------------------------------------#
#           список последних сообщений по каждому заказу                     #
# ---------------------------------------------------------------------------#
@router.get(
    "/",
    response_model=List[MessageOut],
    summary="Последние сообщения каждого заказа",
    dependencies=[Depends(admin_guard)],
)
async def list_last_messages(db: AsyncSession = Depends(get_db)):
    last = (
        select(
            Message.order_id.label("oid"),
            func.max(Message.created_at).label("ts"),
        )
        .group_by(Message.order_id)
        .subquery()
    )
    stmt = (
        select(Message)
        .join(last, and_(Message.order_id == last.c.oid,
                         Message.created_at == last.c.ts))
        .order_by(Message.created_at.desc())
    )
    return (await db.execute(stmt)).scalars().all()


# ---------------------------------------------------------------------------#
#                              ответить на сообщение                          #
# ---------------------------------------------------------------------------#
@router.post(
    "/{message_id}/reply",
    response_model=MessageOut,
    summary="Ответить на сообщение",
    dependencies=[Depends(admin_guard)],
)
async def reply_message(
    message_id: int,
    body: MessageReply,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_user),
):
    try:
        msg = (
            await db.execute(select(Message).where(Message.id == message_id))
        ).scalar_one_or_none()
        if not msg:
            raise HTTPException(404, "Сообщение не найдено")

        msg.reply = body.reply
        msg.replied_at = datetime.utcnow()
        await db.commit()
        await db.refresh(msg)

        await notify_user_about_reply(msg, msg.user_id)
        await notify_admins(msg, admin.id)

        await push_to_order_subscribers(
            order_id=msg.order_id,
            update_type="message_replied",
            data={
                "message_id": msg.id,
                "reply": msg.reply,
                "replied_at": msg.replied_at.isoformat(),
            },
        )

        return msg

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ reply_message: {e}")
        await db.rollback()
        raise HTTPException(500, "Не удалось отправить ответ")


# ---------------------------------------------------------------------------#
#                          удалить одно сообщение                             #
# ---------------------------------------------------------------------------#
@router.delete(
    "/single/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить одно сообщение",
    dependencies=[Depends(admin_guard)],
)
async def delete_single(message_id: int, db: AsyncSession = Depends(get_db)):
    msg = (
        await db.execute(select(Message).where(Message.id == message_id))
    ).scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Сообщение не найдено")

    order_id = msg.order_id
    await db.delete(msg)
    await db.commit()

    await push_to_order_subscribers(
        order_id, "message_deleted",
        {"message_id": message_id, "deleted_by": msg.user_id},
    )


# ---------------------------------------------------------------------------#
#                         удалить весь диалог                                 #
# ---------------------------------------------------------------------------#
@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить весь диалог",
    dependencies=[Depends(admin_guard)],
)
async def delete_chat(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_user),
):
    count = (
        await db.execute(
            select(func.count(Message.id)).where(Message.order_id == order_id)
        )
    ).scalar() or 0
    await db.execute(delete(Message).where(Message.order_id == order_id))
    await db.commit()

    await push_to_order_subscribers(
        order_id, "chat_deleted",
        {"deleted_messages_count": count, "deleted_by": admin.id},
    )
