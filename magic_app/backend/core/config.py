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
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
BACKEND_ENV = BASE_DIR / ".env"
ROOT_ENV    = BASE_DIR.parent / ".env"
BIN_ENV     = BASE_DIR.parent.parent / ".env"  # ← при запуске из бинарника

env_file: str | None = None
for candidate in (BACKEND_ENV, ROOT_ENV, BIN_ENV):
    if candidate.exists():
        env_file = str(candidate)
        log.info("⚙️  .env найден: %s", candidate)
        break
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
        default="postgresql+asyncpg://darina:Myfassa99@176.117.68.16:5432/zerkalodb",
        env="DATABASE_URL",
    )
    BACKEND_API_BASE: AnyHttpUrl | None = Field(None, env="BACKEND_API_BASE")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # --- SSL / TLS settings for Cloudflare Origin certificate ---
    SSL_CERTFILE: str | None = Field(None, env="SSL_CERTFILE")
    SSL_KEYFILE:  str | None = Field(None, env="SSL_KEYFILE")

    # --- Cookie settings ---
    COOKIE_DOMAIN: str | None = Field(None, env="COOKIE_DOMAIN")

    # ---------- валидаторы ----------
    @field_validator("ADMIN_TELEGRAM_IDS", mode="before")
    @classmethod
    def make_list(cls, v: Any) -> List[int]:
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

    @field_validator("COOKIE_DOMAIN", mode="before")
    @classmethod
    def validate_cookie_domain(cls, v: Any) -> str | None:
        """
        Валидация домена для куки
        """
        if v in (None, "", "null", "none"):
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            # Удаляем протокол если он есть
            if v.startswith(("http://", "https://")):
                v = v.split("://", 1)[1]
            # Удаляем слэш в конце
            v = v.rstrip("/")
            # Если домен не начинается с точки, добавляем её для поддоменов
            if not v.startswith(".") and v.count(".") > 0:
                v = f".{v}"
            return v
        return None

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
