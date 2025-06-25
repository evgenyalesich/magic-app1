# bot/main.py
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from dotenv import load_dotenv

# ──────────────────── логирование ────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ─────────────────── переменные среды ────────────────────────
load_dotenv()
TOKEN           = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE        = os.getenv("BACKEND_API_BASE")         # https://api.example.com
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", API_BASE)

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN отсутствует в .env")
if not API_BASE:
    raise RuntimeError("BACKEND_API_BASE отсутствует в .env")

# ─────────────────── aiogram setup ───────────────────────────
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp  = Dispatcher()

# ═════════════════════ /start ════════════════════════════════
@dp.message(F.text == "/start")
async def start_handler(msg: types.Message) -> None:
    tg_id   = msg.from_user.id
    tg_name = msg.from_user.username or msg.from_user.first_name
    log.info("/start from %s (%s)", tg_id, tg_name)

    async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
        await client.post("/api/auth/bot-register",
                          json={"telegram_id": tg_id, "username": tg_name})
        await client.post("/api/auth/login",
                          json={"telegram_id": tg_id, "username": tg_name})

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔮 Войти в волшебный мир",
                    web_app=WebAppInfo(url=FRONTEND_ORIGIN),
                )
            ]
        ]
    )
    await msg.answer(
        "✨ Добро пожаловать! Нажмите кнопку ниже, чтобы открыть приложение.",
        reply_markup=kb,
    )

# ═══════════════ pre-checkout (Stars) ═════════════════════════
@dp.pre_checkout_query()          # type: ignore[attr-defined]
async def pre_checkout(pcq: types.PreCheckoutQuery) -> None:
    """Telegram ждёт подтверждения, иначе платёж зависнет."""
    await bot.answer_pre_checkout_query(
        pcq.id,
        ok=(pcq.currency == "XTR"),     # XTR = Telegram Stars
    )

# ═══════════════ successful_payment ══════════════════════════
@dp.message(F.successful_payment)
async def successful_payment(msg: types.Message) -> None:
    sp = msg.successful_payment
    try:
        payload  = json.loads(sp.invoice_payload)
        order_id = payload.get("order_id")
    except (ValueError, AttributeError):
        order_id = None

    # ▸ уведомляем backend, чтобы он поставил status = paid
    update = {
        "message": {
            "successful_payment": {
                "currency": "XTR",
                "invoice_payload": sp.invoice_payload,
            }
        }
    }
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
        await client.post("/api/payments/webhook", json=update)

    # ▸ сообщаем пользователю, даём кнопку «Открыть заказ»
    if order_id:
        order_url = f"{FRONTEND_ORIGIN}/messages/{order_id}"
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📦 Открыть заказ",
                        web_app=WebAppInfo(url=order_url),
                    )
                ]
            ]
        )
        await msg.answer(
            f"✅ Заказ №<b>{order_id}</b> успешно оплачен!\n"
            "Нажмите кнопку, чтобы открыть диалог заказа.",
            reply_markup=kb,
        )
    else:
        await msg.answer("⭐ Оплата получена! Спасибо!")

# ═══════════════ main loop ═══════════════════════════════════
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Бот остановлен")
