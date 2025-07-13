# backend/api/endpoints/messages.py
import asyncio
import logging
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
from sqlalchemy.orm import joinedload

from backend.api.deps import get_db, get_current_user
from backend.api.websockets.manager import (
    notify_new_message_to_admins as notify_admins,
)

from backend.models.message import Message
from backend.models.order   import Order
from backend.models.user    import User
from backend.schemas.message import MessageCreate, MessageOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/messages", tags=["Messages"])

# ---------------------------------------------------------------------------#
#                               Вспомогательные вещи                           #
# ---------------------------------------------------------------------------#
def _parse_since(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(422, "Параметр since/after должен быть ISO-датой")


async def _check_order_and_rights(
    order_id: int,
    current_user: User,
    db: AsyncSession,
) -> Order:
    order = (
        await db.execute(
            select(Order)
            .options(joinedload(Order.product))
            .where(Order.id == order_id)
        )
    ).scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Заказ не найден")
    if not (current_user.is_admin or order.user_id == current_user.id):
        raise HTTPException(403, "Нет доступа к этому заказу")
    return order


def _inject_product_title(msgs: List[Message]) -> List[Message]:
    for m in msgs:
        if m.order and m.order.product:
            m.product_title = m.order.product.title  # type: ignore[attr-defined]
    return msgs


async def push_to_order_subscribers(order_id: int, update: str, data: dict):
    """Заглушка — пока просто логируем событие."""
    logger.info(f"[polling-mode] order={order_id} update={update} payload={data}")


# ---------------------------------------------------------------------------#
#                       Список чатов (по одному сообщению)                        #
# ---------------------------------------------------------------------------#
@router.get("/", response_model=List[MessageOut])
async def fetch_user_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    last = (
        select(
            Message.order_id.label("order_id"),
            func.max(Message.created_at).label("last_at"),
        )
        .group_by(Message.order_id)
        .subquery()
    )
    stmt = (
        select(Message)
        .join(
            last,
            and_(
                Message.order_id == last.c.order_id,
                Message.created_at == last.c.last_at,
            ),
        )
        .options(joinedload(Message.order).joinedload(Order.product))
        .order_by(Message.created_at.desc())
    )

    # ✅ ИСПРАВЛЕНИЕ: Убрали условие 'if not current_user.is_admin'.
    # Этот эндпоинт для юзеров, поэтому он ВСЕГДА должен фильтровать по ID.
    stmt = stmt.join(Order).where(Order.user_id == current_user.id)

    res = await db.execute(stmt)
    return _inject_product_title(res.scalars().all())


# ---------------------------------------------------------------------------#
#                       История / «хвост» после ?since=…                       #
# ---------------------------------------------------------------------------#
@router.get("/{order_id}", response_model=List[MessageOut])
async def list_messages(
    order_id: int,
    since: Optional[str] = Query(None, description="ISO: вернуть записи ПОЗЖЕ"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = await _check_order_and_rights(order_id, current_user, db)

    ts = _parse_since(since)
    stmt = (
        select(Message)
        .where(Message.order_id == order_id)
        .options(joinedload(Message.order).joinedload(Order.product))
        .order_by(Message.created_at)
    )
    if ts:
        stmt = stmt.where(Message.created_at > ts)

    msgs = (await db.execute(stmt)).scalars().all()

    # welcome, если чат пуст и это первый запрос
    if not msgs and ts is None:
        admin = (
            await db.execute(select(User).where(User.is_admin).limit(1))
        ).scalar_one_or_none()
        sender = admin.id if admin else current_user.id

        welcome = Message(
            user_id=sender,
            order_id=order_id,
            content=(
                "Добрый день! Чтобы получить ваш расклад, "
                "пожалуйста, пришлите ваше имя, дату рождения и ваш вопрос."
            ),
        )
        db.add(welcome)
        await db.commit()
        await db.refresh(welcome)
        welcome.product_title = order.product.title  # type: ignore[attr-defined]
        return [welcome]

    return _inject_product_title(msgs)


# ---------------------------------------------------------------------------#
#                                  LONG-POLL                                  #
# ---------------------------------------------------------------------------#
LONGPOLL_TIMEOUT = 25
CHECK_INTERVAL   = 1

@router.get(
    "/{order_id}/poll",
    response_model=List[MessageOut],
    summary="Long-poll: новые сообщения после ?after",
)
async def poll_messages(
    order_id: int,
    after: Optional[str] = Query(None, description="ISO-метка"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_order_and_rights(order_id, current_user, db)
    ts = _parse_since(after)
    deadline = datetime.utcnow() + timedelta(seconds=LONGPOLL_TIMEOUT)

    while datetime.utcnow() < deadline:
        stmt = select(Message).where(Message.order_id == order_id).order_by(Message.created_at)
        if ts:
            stmt = stmt.where(Message.created_at > ts)

        rows = (await db.execute(stmt)).scalars().all()
        if rows:
            return rows

        await asyncio.sleep(CHECK_INTERVAL)

    return []


# ---------------------------------------------------------------------------#
#                         Создание нового сообщения                           #
# ---------------------------------------------------------------------------#
@router.post("/{order_id}", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def create_message(
    order_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = await _check_order_and_rights(order_id, current_user, db)

    msg = Message(order_id=order_id, user_id=current_user.id, content=payload.content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    await notify_admins(msg, current_user.id)
    await push_to_order_subscribers(order_id, "new_message", {"msg_id": msg.id})

    msg.product_title = order.product.title  # type: ignore[attr-defined]
    return msg


# ---------------------------------------------------------------------------#
#                              Удалить сообщение                              #
# ---------------------------------------------------------------------------#
@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = (
        await db.execute(select(Message).where(Message.id == message_id))
    ).scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Сообщение не найдено")
    if not (current_user.is_admin or msg.user_id == current_user.id):
        raise HTTPException(403, "Нет прав удалять это сообщение")

    await db.delete(msg)
    await db.commit()
    await push_to_order_subscribers(msg.order_id, "message_deleted", {"id": msg.id})

    logger.info(f"[polling-mode] message_deleted id={msg.id} by user={current_user.id}")
    return None
