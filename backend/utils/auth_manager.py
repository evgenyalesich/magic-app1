from __future__ import annotations

"""Telegram WebApp authentication helper.

This module wraps `telegram-webapp-auth`≥3 so the rest of the backend can work
with a tiny, declarative interface while delegating **всю** криптографию
проверки подписи библиотеке.

Key design decisions
--------------------
*   **Нет тяжёлой логики на уровне импорта.**  Бот-токен читается только при
    первом обращении к фабрике, поэтому модуль можно безопасно импортировать
    в тестах без `TELEGRAM_BOT_TOKEN`.
*   **Настраиваемый TTL.**  Передаём его дальше прямо в метод `validate`, чтобы
    библиотеку не патчить.
*   **Статус в виде `(is_valid, user_info)`** под ожидания эндпоинтов.
*   **Singleton-фабрика** наивно кэширует объект, но допускает пересоздание при
    изменении параметров (удобно вpytest).
"""

import dataclasses
import logging
import os
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from telegram_webapp_auth.auth import TelegramAuthenticator, generate_secret_key
from telegram_webapp_auth.errors import ExpiredInitDataError, InvalidInitDataError

log = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_SEC: int = 60 * 60 * 24  # 24 hours


class TelegramAuthManager:  # pylint: disable=too-few-public-methods
    """High-level façade hiding crypto details from the rest of the codebase."""

    __slots__ = ("_auth", "_timeout")

    def __init__(self, *, bot_token: str, timeout_sec: int = _DEFAULT_TIMEOUT_SEC) -> None:
        if not bot_token:
            raise ValueError("bot_token must be provided")

        secret = generate_secret_key(bot_token)
        self._auth: TelegramAuthenticator = TelegramAuthenticator(secret)
        self._timeout: int = timeout_sec

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def authenticate(self, init_data_raw: str) -> Tuple[bool, Dict[str, Any] | None]:
        """Validate *initData* string and extract a flattened `user_info` dict.

        Returns
        -------
        (is_valid, user_info | None)
            * **is_valid**  – ``True`` если подпись и TTL прошли проверку.
            * **user_info** – dict c ключами `id`, `first_name`, ... либо ``None``.
        """
        try:
            init_data_obj = self._auth.validate(
                init_data_raw,
                expr_in=timedelta(seconds=self._timeout) if self._timeout else None,
            )
        except ExpiredInitDataError as exc:
            log.warning("[AUTH_MANAGER] initData expired: %s", exc)
            return False, None
        except InvalidInitDataError as exc:
            log.warning("[AUTH_MANAGER] invalid initData: %s", exc)
            return False, None
        except Exception as exc:  # pragma: no cover – truly unexpected
            log.error("[AUTH_MANAGER] unexpected error: %s", exc, exc_info=True)
            return False, None

        # Flatten dataclass → dict (оставляем только user).
        if init_data_obj.user is None:
            log.warning("[AUTH_MANAGER] initData lacks user block")
            return False, None

        user_info: Dict[str, Any] = dataclasses.asdict(init_data_obj.user)
        return True, user_info


# -------------------------------------------------------------------------
# Factory (simple singleton)
# -------------------------------------------------------------------------
_singleton: Optional[Tuple["TelegramAuthManager", str, int]] = None


def get_telegram_auth_manager(*, bot_token: Optional[str] = None, timeout_sec: int = _DEFAULT_TIMEOUT_SEC) -> "TelegramAuthManager":
    """Return a cached :class:`TelegramAuthManager` instance.

    If called repeatedly with identical params – returns the cached manager.
    Otherwise создаёт новый (удобно для интеграционных тестов).
    """
    global _singleton  # noqa: PLW0603 – intentional module-level cache

    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Telegram bot token must be passed explicitly or via TELEGRAM_BOT_TOKEN env var",
        )

    if _singleton and _singleton[1] == token and _singleton[2] == timeout_sec:
        return _singleton[0]

    manager = TelegramAuthManager(bot_token=token, timeout_sec=timeout_sec)
    _singleton = (manager, token, timeout_sec)
    return manager


# -------------------------------------------------------------------------
# Backwards-compat helper for ad-hoc debugging tools / unit tests.
# -------------------------------------------------------------------------

def parse_and_validate_init_data(init_data_raw: str, *, bot_token: Optional[str] = None) -> Dict[str, Any]:
    """Direct shortcut kept for legacy CLI scripts (⚠️ будет удалён позже)."""
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("bot_token required for parse_and_validate_init_data")

    secret = generate_secret_key(token)
    auth = TelegramAuthenticator(secret)
    return dataclasses.asdict(auth.validate(init_data_raw))


__all__ = [
    "TelegramAuthManager",
    "get_telegram_auth_manager",
    "parse_and_validate_init_data",
]
