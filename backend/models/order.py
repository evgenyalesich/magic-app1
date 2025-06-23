# backend/models/order.py
from __future__ import annotations

from decimal import Decimal
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price:    Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total:    Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default="0",
        comment="Если не передан, считается как quantity * price",
    )

    status:      Mapped[str]      = mapped_column(String(20), nullable=False, server_default="pending")
    created_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # === связи (eager loading) ===
    user:    Mapped[User]      = relationship("User",   back_populates="orders", lazy="selectin")
    product: Mapped[Product]   = relationship("Product",back_populates="orders", lazy="selectin")
    items:   Mapped[list[OrderItem]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # если total не передан — считаем total = quantity * price
        if self.total is None and self.quantity is not None and self.price is not None:
            self.total = Decimal(self.quantity) * Decimal(str(self.price))
