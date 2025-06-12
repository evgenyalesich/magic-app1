import hmac
import hashlib
import time
import logging

from backend.core.config import settings

log = logging.getLogger(__name__)


def verify_telegram_auth(data: dict) -> bool:
    """Проверка Telegram Web-App payload."""
    if "hash" not in data:  # вызов от aiogram-бота
        log.debug("[verify] no hash → bot-register → ok")
        return True

    rec_hash = data.get("hash")
    if not rec_hash:
        log.warning("❌ hash пустой")
        return False

    secret = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    check_str = "\n".join(f"{k}={v}" for k, v in sorted(data.items()) if k != "hash")
    log.debug("[verify] check_string = %s", check_str)

    calc = hmac.new(secret, check_str.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, rec_hash):
        log.warning("❌ hash mismatch: %s ≠ %s", calc, rec_hash)
        return False
    return True


def is_payload_fresh(data: dict, window: int = 300) -> bool:
    ts = data.get("auth_date")
    try:
        ts = int(ts)
    except Exception:
        log.warning("❌ bad auth_date: %s", ts)
        return False
    fresh = abs(time.time() - ts) <= window
    if not fresh:
        log.warning("⏰ payload stale: %s", ts)
    return fresh
