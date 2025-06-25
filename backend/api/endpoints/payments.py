"""
backend/api/endpoints/payments.py
• aiogram ≥ 3.7 — Bot() без parse_mode
• Используем Bot.create_invoice_link()
• Никаких send_invoice / provider_token — фронт сам вызывает
  Telegram.WebApp.openInvoice(), а ссылка приходит строкой
"""

from __future__ import annotations

import json
import logging
import math
import os
from typing import Final

from aiogram import Bot
from aiogram.types import LabeledPrice
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_db
from backend.models.user import User
from backend.schemas.payment import PaymentInit, PaymentInitResponse
from backend.services.crud import order_crud, product_crud

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["Payments"])

# FAQ-курс: 1 ⭐ ≈ 2.015 ₽
STAR_RATE: Final[float] = 2.015

# ─────────────────────────────  POST /payments  ────────────────────────────
@router.post(
    "",
    response_model=PaymentInitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ и вернуть invoice-link для оплаты звёздами",
)
async def init_payment(
    payload: PaymentInit,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    1. Проверяем товар и создаём *pending*-заказ
    2. Считаем стоимость в ⭐ и генерируем ссылку-счёт
    3. Возвращаем `{ order_id, invoice }`, где `invoice` — **строка-URL**
    """

    logger.debug("init_payment: user=%s product=%s",
                 current_user.id, payload.product_id)

    # 1) товар
    product = await product_crud.get(db, id=payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2) заказ
    order = await order_crud.create(
        db,
        obj_in=dict(
            user_id=current_user.id,
            product_id=product.id,
            quantity=1,
            price=float(product.price),
            status="pending",
        ),
    )

    # 3) цена в звёздах (целое число)
    stars = math.ceil(float(product.price) / STAR_RATE)
    prices = [LabeledPrice(label=product.title, amount=stars)]

    # 4) Bot (кешируем в app.state, чтобы не плодить клиент при каждом запросе)
    bot: Bot | None = getattr(request.app.state, "tg_bot", None)
    if bot is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN не задан")
            raise HTTPException(status_code=500, detail="Bot token is not configured")
        bot = Bot(token=token)
        request.app.state.tg_bot = bot
        logger.info("✅ Bot instance initialised")

    # 5) ссылка-инвойс (для Stars provider_token НЕ передаём)
    invoice_link: str = await bot.create_invoice_link(
        title=product.title,
        description=product.description or product.title,
        payload=json.dumps({"order_id": order.id}),
        currency="XTR",
        prices=prices,
    )
    logger.debug("invoice_link for order %s → %s", order.id, invoice_link)

    return PaymentInitResponse(order_id=order.id, invoice=invoice_link)

# ─────────────────────────  POST /payments/webhook  ────────────────────────
@router.post(
    "/webhook",
    summary="Webhook Telegram Payments (XTR)",
    status_code=status.HTTP_200_OK,
)
async def payments_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    • **pre_checkout_query** — подтверждаем, если currency == XTR
    • **successful_payment** — помечаем заказ `paid`
    """
    update: dict = await request.json()
    logger.debug("TG webhook update: %s", update)

    # ---------- pre_checkout_query ----------
    if pre := update.get("pre_checkout_query"):
        ok = pre.get("currency") == "XTR"

        bot: Bot | None = getattr(request.app.state, "tg_bot", None)
        if bot is None:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not token:
                logger.error("No bot token — can't answer pre-checkout")
                return {}
            bot = Bot(token=token)
            request.app.state.tg_bot = bot

        await bot.answer_pre_checkout_query(pre["id"], ok=ok)
        return {}

    # ---------- successful_payment ----------
    msg = update.get("message", {})
    pay = msg.get("successful_payment")
    if pay and pay.get("currency") == "XTR":
        order_id = json.loads(pay["invoice_payload"]).get("order_id")
        logger.info("successful_payment: order %s", order_id)

        if order_id:
            order = await order_crud.get(db, id=order_id)
            if order and order.status == "pending":
                await order_crud.update(db, order, {"status": "paid"})
                logger.info("order %s marked paid", order_id)
        return {}

    # --------- игнорируем всё остальное ---------
    return {}
