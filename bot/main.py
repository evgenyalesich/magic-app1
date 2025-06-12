# bot/main.py
import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import httpx

# ───────────────────────  логирование  ────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ───────────────────────  переменные среды  ───────────────────
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE = os.getenv(
    "BACKEND_API_BASE"
)  # например https://ideas-destination-modify-justin.trycloudflare.com
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", API_BASE)

if not TOKEN:
    raise RuntimeError("⚠️  TELEGRAM_BOT_TOKEN отсутствует в .env")
if not API_BASE:
    raise RuntimeError("⚠️  BACKEND_API_BASE отсутствует в .env")

# ──────────────────────────  aiogram  ─────────────────────────
default_props = DefaultBotProperties(parse_mode="HTML")
bot = Bot(TOKEN, default=default_props)  # ← без parse_mode!
dp = Dispatcher()


# ──────────────────────────  /start  ──────────────────────────
@dp.message(F.text == "/start")
async def start_handler(msg: types.Message) -> None:
    tg_id = msg.from_user.id
    tg_name = msg.from_user.username or msg.from_user.first_name
    log.info("🤖 /start from %s (%s)", tg_id, tg_name)

    async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:

        # 1) bot-register ────────────────────────────────────────────────
        try:
            r = await client.post(
                "/api/auth/bot-register",
                json={"telegram_id": tg_id, "username": tg_name},
            )
            log.info("➡️  bot-register %s", r.status_code)
            r.raise_for_status()
            log.info("✅ Пользователь %s зарегистрирован/обновлён", tg_name)
        except httpx.HTTPError as e:
            log.error("🛑 bot-register failed: %s", e)
            await msg.answer("Ошибка регистрации 😔 Попробуйте позже")
            return

        # 2) login (диагностически) ─────────────────────────────────────
        try:
            login_resp = await client.post(
                "/api/auth/login", json={"telegram_id": tg_id, "username": tg_name}
            )
            log.info("➡️  login %s", login_resp.status_code)
            log.debug("  ↳ %s", login_resp.json())
            login_resp.raise_for_status()
        except httpx.HTTPError as e:
            log.error("🛑 login failed: %s", e)
        # 3) me (диагностически) ────────────────────────────────────────
        try:
            # /me требует cookie, поэтому прокинем tg_id как query-string,
            # чтобы сервер нашёл пользователя напрямую
            me_resp = await client.get("/api/auth/me", params={"tg_id": tg_id})
            log.info("➡️  me %s", me_resp.status_code)
            log.debug("  ↳ %s", me_resp.json() if me_resp.is_success else me_resp.text)
        except httpx.HTTPError as e:
            log.error("🛑 me failed: %s", e)

    # 4) кнопка Web-App  ────────────────────────────────────────────────
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🔮 Войти в волшебный мир",
        web_app=WebAppInfo(url=FRONTEND_ORIGIN),
    )
    log.info("🔗 Web-app URL: %s", FRONTEND_ORIGIN)

    await msg.answer(
        "✨ Добро пожаловать! Нажмите кнопку ниже, чтобы открыть приложение.",
        reply_markup=kb.as_markup(),
    )


# ──────────────────────────  запуск  ───────────────────────────
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("🛑 Бот остановлен")
