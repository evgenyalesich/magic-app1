# backend/api/auth_utils.py

import hmac
import hashlib
import time

from backend.core.config import settings


def verify_telegram_auth(data: dict) -> bool:
    """
    Проверяет правильность Telegram WebApp Login Widget payload.
    Алгоритм (см. документацию Telegram):
      1. Берём все пары key=value, кроме "hash", сортируем по key в лекс порядке.
      2. Склеиваем через '\n'.
      3. Считаем HMAC-SHA256 с ключом = sha256(BOT_TOKEN).digest().
      4. Сравниваем result.hex() с пришедшим data["hash"].

    Возвращает True, если совпало, иначе False.
    """

    received_hash = data.get("hash")
    if not received_hash:
        return False

    # Секретный ключ – sha256 от BOT_TOKEN
    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()

    # Соберём все поля кроме hash
    check_list = []
    for k, v in data.items():
        if k == "hash":
            continue
        # Telegram ожидает, что все значения будут строками
        check_list.append(f"{k}={v}")
    check_list.sort()
    check_string = "\n".join(check_list)

    hmac_obj = hmac.new(secret_key, check_string.encode(), digestmod=hashlib.sha256)
    computed_hash = hmac_obj.hexdigest()

    # Сравниваем через hmac.compare_digest, чтобы защититься от тайм-атак
    return hmac.compare_digest(computed_hash, received_hash)


def is_payload_fresh(data: dict, window: int = 300) -> bool:
    """
    Проверяет, что поле 'auth_date' (UNIX timestamp) не старше, чем `window` секунд.
    Например, window=300 → 5 минут.
    Если поля auth_date нет или оно мешаное/устарело – возвращаем False.
    """
    auth_date = data.get("auth_date")
    if auth_date is None:
        return False
    try:
        timestamp = int(auth_date)
    except (ValueError, TypeError):
        return False

    return abs(time.time() - timestamp) <= window
