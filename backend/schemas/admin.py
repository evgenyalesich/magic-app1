from pydantic import BaseModel

class AdminStats(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    unread_messages: int
