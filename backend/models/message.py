# backend/models/message.py
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(String, nullable=False)

    # Поле для хранения ответа администратора (если есть)
    reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Было: nullable=False, server_default="false"
    # Стало: добавлен Python-дефолт default=False
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,        # Python-сторонний дефолт
        server_default="false"  # дефолт на уровне БД
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    replied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Связи, чтобы можно было доставать last_name пользователя и пр.
    user: Mapped["User"] = relationship("User")
    order: Mapped["Order"] = relationship("Order")
