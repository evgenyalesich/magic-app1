# backend/models/message.py

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)  # <<– добавить
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")
