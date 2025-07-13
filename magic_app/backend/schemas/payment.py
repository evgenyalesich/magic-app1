# backend/schemas/payment.py
# — обновлённые схемы под оплату звёздами через Telegram

from pydantic import BaseModel, ConfigDict, Field

# Общая конфигурация: разрешаем создавать модели из ORM-объектов
ORM_CONFIG = ConfigDict(from_attributes=True)

class PaymentInit(BaseModel):
    """
    Запрос от фронта: какой товар и в каком количестве хотим оплатить.
    """
    model_config = ORM_CONFIG

    product_id: int = Field(
        ...,
        description="ID товара для заказа"
    )
    quantity: int = Field(
        1,
        ge=1,
        description="Количество единиц товара (минимум 1)"
    )

class PaymentInitResponse(BaseModel):
    """
    Ответ бэка: order_id + ссылка на invoice.
    """
    model_config = ORM_CONFIG

    order_id: int = Field(
        ...,
        description="ID созданного заказа"
    )
    invoice: str = Field(
        ...,
        description="URL-ссылка на оплату (Telegram Invoice Link)"
    )
class OrderStatusResponse(BaseModel):
    order_id: int
    status: str
