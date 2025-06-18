"""
Просто парсим initData от Telegram WebApp и вытаскиваем user.

Больше никаких HMAC, hash, signature и т.п.
"""
import json
import logging
from typing import Dict, Optional
from urllib.parse import parse_qsl

log = logging.getLogger(__name__)


class TelegramWebAppAuth:
    """Простейший разбор initData без проверки подписи."""

    def extract_user(self, raw_init_data: str) -> Optional[Dict]:
        """
        raw_init_data — строка вида "k1=v1&user=…&auth_date=…&hash=…"
        Парсим её, достаём параметр `user` и JSON-декодим.
        Если user нет или JSON упадёт — возвращаем None.
        """
        try:
            params = dict(parse_qsl(raw_init_data, keep_blank_values=True))
            user_raw = params.get("user")
            if not user_raw:
                log.warning("No `user` field in initData")
                return None
            return json.loads(user_raw)
        except Exception as e:
            log.exception("Failed to extract user from initData: %s", e)
            return None


def create_telegram_auth() -> TelegramWebAppAuth:
    return TelegramWebAppAuth()
