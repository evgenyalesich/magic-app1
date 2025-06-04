import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не задан TELEGRAM_BOT_TOKEN в переменных окружения!")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id  # <-- теперь int, а не str
    username = message.from_user.username or message.from_user.first_name

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://jacket-days-easter-bald.trycloudflare.com/api/auth/login",
            json={"telegram_id": telegram_id, "username": username},
        )

        if response.status_code == 200:
            logging.info(f"✅ Пользователь {username} зарегистрирован.")
        else:
            logging.error(
                f"Ошибка авторизации: {response.status_code}, {response.text}"
            )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔮 Войти в волшебный мир",
        web_app=WebAppInfo(url="https://jacket-days-easter-bald.trycloudflare.com"),
    )

    await message.answer(
        "✨ Добро пожаловать! Нажмите на кнопку ниже, чтобы войти в приложение",
        reply_markup=keyboard.as_markup(),
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
