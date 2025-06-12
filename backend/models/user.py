from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger
from datetime import datetime
from backend.models.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger(), unique=True, index=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    total_orders: Mapped[int] = mapped_column(default=0)
    total_spent: Mapped[float] = mapped_column(default=0.0)
    is_admin: Mapped[bool] = mapped_column(default=False)
    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    messages = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )
