# backend/models/user.py
from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, DateTime, Float, Integer, String, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=True
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=True
    )

    # эти два поля могут ещё не существовать в БД — допишем миграцию ниже
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin:  Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spent:  Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    orders = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )
