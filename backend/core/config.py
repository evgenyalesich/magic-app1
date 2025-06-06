import os
from dotenv import load_dotenv
from pydantic import BaseSettings
from typing import List

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:6628@localhost:5433/darina_db"
)


class Settings(BaseSettings):
    BOT_TOKEN: str  # вместо TELEGRAM_BOT_TOKEN
    ADMIN_TG_IDS: List[int]  # вместо ADMIN_TELEGRAM_ID
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
