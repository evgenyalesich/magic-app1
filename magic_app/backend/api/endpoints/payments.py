from __future__ import annotations

import json
import logging
import math
import os
from typing import Final
from decimal import Decimal # Импортируем Decimal для проверки типов

from aiogram import Bot
from aiogram.types import LabeledPrice
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_db
from backend.models.order import Order
from backend.models.user import User
from backend.schemas.payment import PaymentInit, PaymentInitResponse, OrderStatusResponse
from backend.services.crud import order_crud, product_crud

# Настраиваем подробное логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter() # Префикс теперь задается в api.py

# Курс конвертации рублей в Telegram Stars (1 ⭐ ≈ 2.015 ₽)
STAR_RATE: Final[float] = 2.015


# ─────────────────────────── helpers ────────────────────────────
async def _get_bot(request: Request) -> Bot:
    """Синглтон-bot в `app.state`."""
    bot: Bot | None = getattr(request.app.state, "tg_bot", None)
    if bot is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN env missing. Cannot initialize bot.")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Bot token is not configured")
        bot = Bot(token=token)
        request.app.state.tg_bot = bot
        logger.info("✅ Telegram-bot initialized successfully.")
    return bot


async def _build_invoice_link(
    *,
    bot: Bot,
    product_title: str,
    product_descr: str,
    amount_rub: Decimal,  # Цена из БД приходит как Decimal
    order_id: int,
) -> str:
    """Конвертируем ₽→⭐ и отдаём invoice-URL."""
    stars_amount = math.ceil(float(amount_rub) / STAR_RATE)
    logger.info(f"Order #{order_id}: Converting {amount_rub} RUB to {stars_amount} XTR.")

    prices = [LabeledPrice(label=product_title, amount=stars_amount)]

    payload = json.dumps({"order_id": order_id})
    logger.info(f"Order #{order_id}: Creating invoice link with payload: {payload}")

    link = await bot.create_invoice_link(
        title=product_title,
        description=product_descr,
        payload=payload,
        currency="XTR",
        prices=prices,
    )
    logger.info(f"Order #{order_id}: Successfully created invoice link.")
    return link


# ───────────────────── POST / (ОСНОВНОЙ ПУТЬ) ──────────────────────
@router.post(
    "/",
    response_model=PaymentInitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ и получить ссылку на оплату",
)
async def create_order_and_invoice(
    payment_data: PaymentInit,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        f"User {current_user.telegram_id} initiated payment for product_id={payment_data.product_id} "
        f"with quantity={payment_data.quantity}."
    )

    product = await product_crud.get(db, id=payment_data.product_id)
    if not product:
        logger.warning(f"Product with id={payment_data.product_id} not found.")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

    total_price = product.price * payment_data.quantity
    logger.info(f"Found product '{product.title}'. Total price: {total_price} RUB.")

    order_in = {
        "user_id": current_user.id,
        "product_id": product.id,
        "quantity": payment_data.quantity,
        "price": total_price,
        "status": "pending",
    }
    new_order = await order_crud.create(db, obj_in=order_in)
    logger.info(f"Created new order #{new_order.id} with status 'pending' for user {current_user.telegram_id}.")

    try:
        bot = await _get_bot(request)
        invoice_link = await _build_invoice_link(
            bot=bot,
            product_title=product.title,
            product_descr=product.description or product.title,
            amount_rub=new_order.price,
            order_id=new_order.id,
        )
        return PaymentInitResponse(order_id=new_order.id, invoice=invoice_link)
    except Exception as e:
        logger.error(f"Failed to create invoice for new order #{new_order.id}: {e}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create invoice")


# ── POST /{order_id}/stars (invoice для уже созданного pending-заказа) ──
@router.post(
    "/{order_id}/stars",
    response_model=PaymentInitResponse,
    summary="Invoice-ссылка для уже существующего `pending`-заказа",
)
async def stars_invoice_for_order(
    order_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Stars invoice explicitly requested for order #{order_id} by user {current_user.telegram_id}.")

    order: Order | None = await order_crud.get(db, id=order_id)
    if not order:
        logger.warning(f"Order #{order_id} not found for user {current_user.telegram_id}.")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.user_id != current_user.id:
        logger.error(f"User {current_user.telegram_id} attempted to access order #{order_id} owned by another user.")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied to this order")

    if order.status != "pending":
        logger.warning(f"Order #{order_id} is not pending (current status: {order.status}). Cannot create new invoice.")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Order status is '{order.status}', not 'pending'.")

    product = await product_crud.get(db, id=order.product_id)
    if not product:
        logger.error(f"FATAL: Product {order.product_id} not found for existing order #{order_id}!")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product associated with this order not found")

    try:
        bot = await _get_bot(request)
        invoice_link = await _build_invoice_link(
            bot=bot,
            product_title=product.title,
            product_descr=product.description or product.title,
            amount_rub=order.price,
            order_id=order.id,
        )
        return PaymentInitResponse(order_id=order.id, invoice=invoice_link)
    except Exception as e:
        logger.error(f"Error creating stars invoice for existing order #{order_id}: {e}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create invoice")


# ── GET /{order_id}/status (проверка статуса для фронтенда) ──
@router.get(
    "/{order_id}/status",
    response_model=OrderStatusResponse,
    summary="Получить статус заказа для проверки оплаты",
)
async def get_order_status(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(f"User {current_user.telegram_id} is checking status for order #{order_id}.")

    order = await order_crud.get(db, id=order_id)

    if not order or order.user_id != current_user.id:
        logger.warning(f"Failed status check: Order #{order_id} not found or access denied for user {current_user.telegram_id}.")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found or access denied")

    logger.debug(f"Order #{order_id} current status is '{order.status}'.")
    return OrderStatusResponse(order_id=order.id, status=order.status)


# ────────────────────────  POST /webhook (вебхук от Telegram) ─────────────────────────
@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Webhook для Telegram Payments (XTR)",
    include_in_schema=False,
)
async def payments_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        update_data = await request.json()
        logger.debug("[WEBHOOK] Received update from Telegram: %s", update_data)

        if pre_checkout_query := update_data.get("pre_checkout_query"):
            # ... (pre-checkout logic is correct) ...
            return {}

        if message := update_data.get("message"):
            if successful_payment := message.get("successful_payment"):
                # ... (payment parsing logic is correct) ...
                payload_str = successful_payment.get("invoice_payload", "{}")
                payload = json.loads(payload_str)
                order_id = payload.get("order_id")

                logger.info(f"✅ [WEBHOOK] Received successful_payment for order_id={order_id}.")

                if not order_id:
                    logger.error("[WEBHOOK] ❌ No order_id in payload.")
                    return {}

                order = await order_crud.get(db, id=order_id)

                if not order:
                    logger.error(f"[WEBHOOK] ❌ Order #{order_id} not found!")
                    return {}

                if order.status != "pending":
                    logger.warning(f"[WEBHOOK] ⚠️ Order #{order_id} already processed. Status: '{order.status}'.")
                    return {}

                try:
                    logger.info(f"[WEBHOOK] Updating status for order #{order_id} to 'paid'...")
                    # ✅ ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ: Убираем именованный аргумент `db_obj`.
                    await order_crud.update(db, order, {"status": "paid"})
                    logger.info(f"[WEBHOOK] ✅✅✅ SUCCESS! Order #{order_id} status updated to 'paid'.")
                except Exception as e:
                    logger.error(
                        f"[WEBHOOK] ❌ CRITICAL ERROR updating order #{order_id} status!",
                        exc_info=True
                    )

                return {}

        logger.info("[WEBHOOK] Update received, but it was not a payment-related update. Ignored.")
        return {}

    except json.JSONDecodeError as e:
        logger.error(f"[WEBHOOK] ❌ JSONDecodeError: {e}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON received")
    except Exception as e:
        logger.error(f"[WEBHOOK] ❌ General webhook processing error: {e}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Webhook processing failed")
