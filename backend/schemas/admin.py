# backend/schemas/admin.py
from pydantic import BaseModel, ConfigDict


ORM_CONFIG = ConfigDict(from_attributes=True)


class AdminStats(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    unread_messages: int

    model_config = ORM_CONFIG
