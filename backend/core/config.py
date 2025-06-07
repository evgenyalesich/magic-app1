from dotenv import load_dotenv
from typing import List

from pydantic import Field  # <— вот это
from pydantic_settings import BaseSettings

# Загружаем .env
load_dotenv()


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    ADMIN_TELEGRAM_IDS: List[int] = Field(default_factory=list)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:6628@localhost:5433/darina_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
