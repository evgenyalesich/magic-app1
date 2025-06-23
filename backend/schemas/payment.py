from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

# Общая конфигурация для всех схем (чтение из ORM)
ORM_CONFIG = ConfigDict(from_attributes=True)

class PaymentInit(BaseModel):
    product_id: int
    model_config = ORM_CONFIG

class PaymentInitResponse(BaseModel):
    order_id: int
    options: List[str]
    stars_required: int = Field(..., description="Сколько звёзд нужно для оплаты")
    rate: float = Field(2.015, description="Курс: 1 звезда = X ₽")
    model_config = ORM_CONFIG

class PaymentWithStars(BaseModel):
    order_id: int
    # Make stars_to_use optional since your logic handles None case
    stars_to_use: Optional[int] = Field(None, description="Сколько звёзд списать при оплате")
    model_config = ORM_CONFIG
