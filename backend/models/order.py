# backend/models/order.py
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Order(Base):
    __tablename__ = "orders"

    # --- FK & основные поля ------------------------------------------------
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # 👉 новое поле
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default="0",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # --- relationships -----------------------------------------------------
    user = relationship("User", back_populates="orders")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    # --- auto-fill total ----------------------------------------------------
    def __init__(self, **kw):
        super().__init__(**kw)

        # если total не передали вручную → считаем сами
        if self.total is None:
            self.total = Decimal(str(self.quantity)) * Decimal(str(self.price))
