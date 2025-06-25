"""
backend/schemas/payment.py  — обновлённые схемы под оплату звёздами через Telegram

Изменения:
• PaymentInitResponse теперь содержит только `order_id` и `invoice` (словарь).
• Модель PaymentWithStars удалена — списание звёзд происходит на стороне Telegram.
"""

from typing import Dict
from pydantic import BaseModel, ConfigDict, Field

# Общая конфигурация: разрешаем создавать модели из ORM-объектов
ORM_CONFIG = ConfigDict(from_attributes=True)


class PaymentInit(BaseModel):
    """Запрос от фронта: какой товар хотим оплатить."""

    product_id: int
    model_config = ORM_CONFIG


class PaymentInitResponse(BaseModel):
    """Ответ backend'а: order_id + invoice.

    `invoice` — словарь с полями Bot API (provider_token, currency, …),
    который фронт передаст в `Telegram.WebApp.openInvoice(...)`.
    """

    order_id: int
    invoice:  str


    model_config = ORM_CONFIG
