# backend/core/config.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings

log = logging.getLogger(__name__)

# ────────── .env ──────────
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
BACKENDENV = BASE_DIR / ".env"
ROOTENV = BASE_DIR.parent / ".env"

env_file: str | None = None
if BACKENDENV.exists():
    env_file = str(BACKENDENV)
    log.info(".env найден: %s", BACKENDENV)
elif ROOTENV.exists():
    env_file = str(ROOTENV)
    log.info(".env найден в корне проекта: %s", ROOTENV)
else:
    log.warning(".env не найден – TELEGRAM_BOT_TOKEN обязателен")

if env_file:
    load_dotenv(env_file)


# ────────── Settings ──────────
class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    BOT_TOKEN: str | None = None  # alias
    ADMIN_TELEGRAM_IDS: List[int] = Field(
        default_factory=list,
        env="ADMIN_TELEGRAM_IDS",
    )

    # DB
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:6628@localhost:5433/darina_db",
        env="DATABASE_URL",
    )

    # Front / Back
    FRONTEND_ORIGIN: AnyHttpUrl = Field(..., env="FRONTEND_ORIGIN")
    BACKEND_API_BASE: AnyHttpUrl | None = Field(None, env="BACKEND_API_BASE")

    # Misc
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # ---------- validators ----------
    @field_validator("ADMIN_TELEGRAM_IDS", mode="before")
    @classmethod
    def _split_ids(cls, v):

        if v in (None, "", []):
            return []

        if isinstance(v, int):
            return [v]

        if isinstance(v, str):
            v = v.replace(" ", "").split(",")

        # iterable → приводим всё к int
        try:
            return [int(item) for item in v if str(item).strip()]
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Не могу разобрать ADMIN_TELEGRAM_IDS: {v}") from exc

    @field_validator("BOT_TOKEN", mode="after")
    @classmethod
    def _fallback_to_main(cls, v, info):
        return v or info.data.get("TELEGRAM_BOT_TOKEN")

    # pydantic-config
    model_config = {
        "env_file": env_file,
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "forbid",  # любая лишняя переменная в .env → сразу ошибка
    }


# инициализируем при импорте
try:
    settings = Settings()
    log.info("✅ Settings загружены")
except Exception:
    log.exception("❌ Ошибка загрузки настроек – проверьте .env")
    raise
