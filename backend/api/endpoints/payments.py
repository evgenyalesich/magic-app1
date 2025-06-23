# backend/api/endpoints/payments.py
import json
import math
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps        import get_db, get_current_user
from backend.models.user     import User
from backend.services.crud   import order_crud, product_crud, message_crud, user_crud
from backend.schemas.payment import (
    PaymentInit,
    PaymentInitResponse,
    PaymentWithStars,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["Payments"])

# курс рубль → звезда
STAR_RATE = 2.015  # ₽ за 1 звезду

@router.post(
    "",
    response_model=PaymentInitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Инициация оплаты: создаём заказ и возвращаем способы оплаты"
)
async def init_payment(
    payload: PaymentInit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug("init_payment called: user=%s product_id=%s", current_user.id, payload.product_id)
    product = await product_crud.get(db, id=payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    order = await order_crud.create(db, obj_in={
        "user_id":  current_user.id,
        "product_id": payload.product_id,
        "quantity":   1,
        "price":      float(product.price),
        "status":     "pending",
    })
    stars_required = math.ceil(float(product.price) / STAR_RATE)
    logger.debug("Stars required for order %s: %s (rate=%s)", order.id, stars_required, STAR_RATE)

    return PaymentInitResponse(
        order_id=order.id,
        options=["stars", "frikassa"],
        stars_required=stars_required,
        rate=STAR_RATE,
    )

@router.post(
    "/stars",
    status_code=status.HTTP_200_OK,
    summary="Оплата заказа реальными звёздами",
)
async def pay_with_stars(
    payload: PaymentWithStars,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug("pay_with_stars called: user=%s payload=%s", current_user.id, payload.dict())
    order = await order_crud.get(db, id=payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order already paid or in invalid status")

    price_rub = float(order.price)
    required_stars = math.ceil(price_rub / STAR_RATE)
    to_deduct = payload.stars_to_use or required_stars
    if to_deduct < required_stars:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stars specified. Required: {required_stars}, provided: {to_deduct}"
        )

    user = await user_crud.get(db, id=current_user.id)
    if not user or user.stars < to_deduct:
        logger.warning("Not enough stars: user=%s has=%s wants=%s", current_user.id, getattr(user, "stars", 0), to_deduct)
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stars on your balance. Required: {to_deduct}, available: {getattr(user, 'stars', 0)}"
        )

    new_balance = user.stars - to_deduct
    await user_crud.update(db, user, {"stars": new_balance})
    paid_order = await order_crud.update(db, order, {"status": "paid"})
    await message_crud.create(db, obj_in={
        "order_id": paid_order.id,
        "user_id":  current_user.id,
        "content": (
            f"Спасибо за оплату {to_deduct} звёздами ({STAR_RATE}₽=1★). "
            f"Ваш заказ #{paid_order.id} оплачен!"
        ),
    })

    return {
        "order_id":        paid_order.id,
        "status":          paid_order.status,
        "stars_deducted":  to_deduct,
        "stars_remaining": new_balance,
    }

@router.post(
    "/webhook",
    summary="Webhook для обработки Telegram Payments (XTR)",
    status_code=status.HTTP_200_OK,
)
async def payments_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    update = await request.json()
    logger.debug("Telegram webhook update: %s", update)

    # 1) Pre-checkout — разрешаем списание XTR
    if pre := update.get("pre_checkout_query"):
        query_id = pre["id"]
        currency = pre["currency"]
        if currency == "XTR":
            # answerPreCheckoutQuery
            await request.app.state.tg_bot.answer_pre_checkout_query(pre["id"], ok=True)
            logger.info("Approved pre_checkout_query %s for XTR", query_id)
        else:
            await request.app.state.tg_bot.answer_pre_checkout_query(pre["id"], ok=False,
                error_message="Unsupported currency")
            logger.warning("Rejected pre_checkout_query %s: currency=%s", query_id, currency)
        return {}

    # 2) Успешная оплата
    msg = update.get("message", {})
    payment = msg.get("successful_payment")
    if payment:
        payload = json.loads(payment["invoice_payload"])  # тут лежит {"order_id": ...}
        order_id = payload["order_id"]
        currency = payment["currency"]
        logger.info("Received successful_payment for order %s in %s", order_id, currency)

        if currency != "XTR":
            logger.error("Unexpected currency in successful_payment: %s", currency)
            return {}

        # отмечаем заказ как оплаченный
        order = await order_crud.get(db, id=order_id)
        if not order:
            logger.error("Order %s not found on successful_payment", order_id)
            return {}
        await order_crud.update(db, order, {"status": "paid"})
        # чтобы не дублировать сообщения, можно здесь ничего не шлём —
        # текст уже ушёл из frontend
        logger.info("Order %s marked as paid", order_id)
        return {}

    # всё остальное
    return {}
