from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)

# ─────────────────── поиск .env ───────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
BACKEND_ENV = BASE_DIR / ".env"
ROOT_ENV = BASE_DIR.parent / ".env"

env_file: str | None = None
if BACKEND_ENV.exists():
    env_file = str(BACKEND_ENV)
    log.info("⚙️  .env найден: %s", BACKEND_ENV)
elif ROOT_ENV.exists():
    env_file = str(ROOT_ENV)
    log.info("⚙️  .env найден в корне: %s", ROOT_ENV)
else:
    log.warning("⚠️  .env не найден – без TELEGRAM_BOT_TOKEN не запустится")

if env_file:
    load_dotenv(env_file)

# ─────────────────── модель настроек ───────────────
class Settings(BaseSettings):
    # --- обязательные ---
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    FRONTEND_ORIGIN:    AnyHttpUrl = Field(..., env="FRONTEND_ORIGIN")

    # --- необязательные / со значениями по-умолчанию ---
    ADMIN_TELEGRAM_IDS: List[int] = Field(default_factory=list, env="ADMIN_TELEGRAM_IDS")
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:6628@localhost:5433/darina_db",
        env="DATABASE_URL",
    )
    BACKEND_API_BASE: AnyHttpUrl | None = Field(None, env="BACKEND_API_BASE")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # ---------- валидаторы ----------
    @field_validator("ADMIN_TELEGRAM_IDS", mode="before")
    @classmethod
    def _make_list(cls, v: Any) -> List[int]:
        """
        > ADMIN_TELEGRAM_IDS=1,2,3  →  [1,2,3]
        > ADMIN_TELEGRAM_IDS=        →  []
        """
        if v in (None, "", []):
            return []
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            v = v.replace(" ", "").split(",")
        try:
            return [int(i) for i in v if str(i).strip()]
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Не могу разобрать ADMIN_TELEGRAM_IDS: {v}") from exc

    # ---------- pydantic-конфиг ----------
    model_config = SettingsConfigDict(
        env_file=env_file or ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",           # ← важно!
    )


# ─────────────────── инициализация ─────────────────
try:
    settings = Settings()
    log.info("✅ Settings загружены\n%s", settings.model_dump())
except Exception:
    log.exception("❌ Ошибка загрузки настроек – проверьте .env")
    raise
