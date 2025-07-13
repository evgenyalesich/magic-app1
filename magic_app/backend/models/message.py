# backend/models/message.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    select,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    column_property,
)

from .base import Base
from .order import Order
from .product import Product
from .user import User


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

    # ответ администратора (может отсутствовать)
    reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # непрочитанное по умолчанию
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    replied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ───────────────── relationships ─────────────────
    user:  Mapped["User"]  = relationship("User")
    order: Mapped["Order"] = relationship("Order")

    # ─────────── column_property для product_title ───────────
    # теперь через JOIN orders→products
    product_title: Mapped[Optional[str]] = column_property(
        select(Product.title)
        .join(Order, Order.product_id == Product.id)
        .where(Order.id == order_id)  # correlate on message.order_id
        .correlate_except(Product, Order)
        .scalar_subquery()
    )

    # ─────────── column_property для user_name ───────────
    user_name: Mapped[Optional[str]] = column_property(
        select(User.username)
        .where(User.id == user_id)
        .correlate_except(User)
        .scalar_subquery()
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Message id={self.id} order={self.order_id} "
            f"user={self.user_id} read={self.is_read}>"
        )
