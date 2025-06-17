import hashlib
import hmac
import logging
from time import time
from urllib.parse import parse_qsl

from backend.core.config import settings

log = logging.getLogger(__name__)

# ❗️ секрет – это САМ ТОКЕН, без каких-либо хешей
_SECRET: bytes = hmac.new(
    key=b"WebAppData",
    msg=settings.TELEGRAM_BOT_TOKEN.encode(),
    digestmod=hashlib.sha256
).digest()


_TTL = 24 * 3600     # допустимый «возраст» initData (секунды)


def _hmac_sha256_hex(secret: bytes, msg: str) -> str:
    """Возвращает hex-строку HMAC-SHA256(secret, msg)."""
    return hmac.new(secret, msg.encode(), hashlib.sha256).hexdigest()


def _build_data_check_string(raw: str) -> tuple[str, dict]:
    """
    Формирует строку, по которой Telegram считает подпись.

    Берём все «k=v» кроме --> hash и signature,
    сортируем по key, соединяем через «\n».
    """
    pairs = [
        (k, v)
        for k, v in parse_qsl(raw, keep_blank_values=True)
        if k not in ("hash", "signature")
    ]
    pairs.sort(key=lambda p: p[0])
    dcs = "\n".join(f"{k}={v}" for k, v in pairs)
    return dcs, dict(pairs)


def verify_telegram_auth(init_params: dict[str, str]) -> bool:
    """
    Проверяет Telegram Web-App payload.

    init_params — уже распарсенный словарь {"query_id": "...", "user": "...", ...}
    """
    try:
        # превращаем обратно в строку вида k=v&k=v…
        raw = "&".join(f"{k}={v}" for k, v in init_params.items())
        dcs, _ = _build_data_check_string(raw)

        recv_hash = init_params.get("hash", "")
        calc_hash = _hmac_sha256_hex(_SECRET, dcs)

        log.debug("[verify]\ndata_check_string:\n%s", dcs)
        log.debug("received_hash=%s", recv_hash)
        log.debug("computed_hash=%s", calc_hash)

        return hmac.compare_digest(calc_hash, recv_hash)
    except Exception as exc:        # noqa: BLE001
        log.exception("verify_telegram_auth failed: %s", exc)
        return False


def is_payload_fresh(parsed: dict) -> bool:
    """Проверяем поле auth_date на «свежесть»."""
    try:
        return (time() - int(parsed["auth_date"])) < _TTL
    except Exception:               # noqa: BLE001
        return False
