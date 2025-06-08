import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не задан TELEGRAM_BOT_TOKEN в переменных окружения!")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    """
    Просто выдаём кнопку WebApp.
    Линк на фронтенд, где React уже подхватит
    Telegram.WebApp.initData и сделает POST /api/auth/login.
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔮 Войти в Magic App",
        web_app=WebAppInfo(url="https://atlantic-reduces-fame-also.trycloudflare.com"),
    )

    await message.answer(
        "✨ Добро пожаловать в Magic App! Нажмите кнопку ниже, чтобы войти",
        reply_markup=keyboard.as_markup(),
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
