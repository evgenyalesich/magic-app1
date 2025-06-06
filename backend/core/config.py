import os
from dotenv import load_dotenv
from pydantic import BaseSettings
from typing import List


load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:6628@localhost:5433/test_pass"
)


class Settings(BaseSettings):
    DATABASE_URL: str

    # Вот наш Telegram-бот-токен (суть: нужен, чтобы проверить хэш из WebApp auth)
    TELEGRAM_BOT_TOKEN: str

    # Список Telegram-ID, которые считаются админами
    ADMIN_TELEGRAM_ID: List[int]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
