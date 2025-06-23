# backend/schemas/admin.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class AdminMessageWithExtras(BaseModel):
    id: int
    order_id: int
    content: str
    reply: Optional[str]
    is_read: bool
    created_at: datetime
    replied_at: Optional[datetime]
    user_name: str
    product_title: str

    # Pydantic v2: tell it to read from ORM attributes
    model_config = ConfigDict(from_attributes=True)
