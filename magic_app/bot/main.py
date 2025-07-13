"""
Telegram Bot для приложения "Зеркало Судьбы"
Обрабатывает регистрацию пользователей и платежи через Telegram Stars
"""
import asyncio
import json
import logging
import os
import sys
import time
import hmac
import hashlib
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlencode, quote, unquote_plus

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ],
)
log = logging.getLogger(__name__)

# --- 1. ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ И ИХ ЛОГИРОВАНИЕ ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE = os.getenv("BACKEND_API_BASE")
WEB_APP_URL = os.getenv("WEB_APP_URL")

log.info("--- [БОТ] ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ---")
log.info("[БОТ] Загружен токен: %s", TOKEN)
log.info("[БОТ] Адрес бэкенда (API_BASE): %s", API_BASE)
log.info("[БОТ] Адрес веб-приложения (WEB_APP_URL): %s", WEB_APP_URL)

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN отсутствует в .env")
if not API_BASE:
    raise RuntimeError("BACKEND_API_BASE отсутствует в .env")
if not WEB_APP_URL:
    raise RuntimeError("WEB_APP_URL отсутствует в .env")
log.info("--- [БОТ] Все переменные окружения успешно загружены ---")

# Инициализация бота
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Пути к файлам
BOT_DIR = Path(__file__).parent
PHOTO_PATH = BOT_DIR / "f1fb9a23-5f67-4679-96dc-a58601f62203.png"


# --- 2. УЛУЧШЕННАЯ ФУНКЦИЯ ГЕНЕРАЦИИ ХЕША ДЛЯ ОТЛАДКИ ---
def make_tg_hash(data: dict[str, str | int]) -> str:
    """
    Создает hash для аутентификации пользователя, используя метод WebApp.
    СИНХРОНИЗИРОВАНО С БЭКЕНДОМ!
    """
    log.info("=== [БОТ] НАЧАЛО СОЗДАНИЯ ХЕША (для /debug_hash) ===")
    log.info("[БОТ] Входные данные make_tg_hash: %s", data)

    data_for_hash = {k: v for k, v in data.items() if k != 'hash'}

    parts = []
    log.info("--- [БОТ] Формирование строки для проверки (сортировка по ключам) ---")

    sorted_keys_log = ", ".join(sorted(data_for_hash.keys()))
    log.info("[БОТ] Отсортированные ключи для хеширования: %s", sorted_keys_log)

    for key in sorted(data_for_hash.keys()):
        value = data_for_hash[key]

        if isinstance(value, bool):
            value = str(value).lower()
        elif value is not None:
            value = str(value)

        if value is not None:
            log.info("[БОТ] Добавляем к строке: '%s' = '%s'", key, value)
            parts.append(f"{key}={value}")
        else:
            log.warning("[БОТ] ПРОПУЩЕНО поле '%s' (None)", key)

    data_check_string = "\n".join(parts)
    log.info("--- [БОТ] Итоговая строка для хеширования ---\n%s\n---", data_check_string)

    log.info("[БОТ] Длина итоговой строки (байты, utf-8): %d", len(data_check_string.encode('utf-8')))


    log.info("--- [БОТ] Генерация секретного ключа ---")
    log.info("[БОТ] Используется токен, начинающийся с: '%s...'", TOKEN[:12])

    secret_key = hmac.new(
        key=TOKEN.encode('utf-8'),
        msg=b"WebAppData",
        digestmod=hashlib.sha256
    ).digest()
    log.info("[БОТ] Секретный ключ (hex): %s", secret_key.hex())

    log.info("--- [БОТ] Расчет финального хеша ---")
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    log.info("[БОТ] Рассчитанный хеш: %s", calculated_hash)
    log.info("=== [БОТ] КОНЕЦ СОЗДАНИЯ ХЕША ===")
    return calculated_hash


async def make_api_request(endpoint: str, payload: dict, headers: Optional[dict] = None) -> Optional[dict]:
    """
    Универсальная функция для API запросов с обработкой ошибок
    """
    log.info("=== [БОТ] API ЗАПРОС ===")
    log.info("Endpoint: %s", endpoint)
    log.info("Payload: %s", payload)

    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=30) as client:
            response = await client.post(endpoint, json=payload, headers=headers or {})

            log.info("Статус ответа: %d", response.status_code)
            log.info("Тело ответа: %s", response.text)

            response.raise_for_status()
            result = response.json() if response.content else None
            log.info("Успешный ответ: %s", result)
            return result

    except httpx.HTTPStatusError as e:
        log.error("HTTP ошибка %s при запросе к %s", e.response.status_code, endpoint)
        log.error("Тело ошибки: %s", e.response.text)
        return None
    except Exception as e:
        log.error("Ошибка при запросе к %s: %s", endpoint, e)
        return None


@dp.message(F.text == "/start")
async def start_handler(msg: types.Message) -> None:
    """
    Обработчик команды /start
    """
    user = msg.from_user
    if not user:
        await msg.answer("❌ Ошибка получения данных пользователя")
        return

    log.info("=== [БОТ] ОБРАБОТКА /start ===")
    log.info("Пользователь: ID=%s, username=%s", user.id, user.username)


    caption = (
        "✨ <b>Добро пожаловать в «Зеркало Судьбы»!</b>\n\n"
        "🔮 Здесь ты найдёшь ответы на самые волнующие вопросы о своей жизни!\n\n"
        "📱 Для продолжения откройте веб-приложение."
    )

    try:
        if PHOTO_PATH.exists():
            await msg.answer_photo(
                FSInputFile(PHOTO_PATH),
                caption=caption,

            )
        else:
            await msg.answer(
                caption,

            )
        log.info("✅ Сообщение со ссылкой на WebApp отправлено пользователю %s", user.id)
    except TelegramBadRequest as e:
        log.error("❌ Ошибка отправки сообщения в Telegram: %s", e)
        await msg.answer("Произошла ошибка при запуске WebApp. Пожалуйста, попробуйте позже.")
    except Exception as e:
        log.exception("❌ Неизвестная ошибка в start_handler: %s", e)
        await msg.answer("Произошла неизвестная ошибка. Пожалуйста, попробуйте позже.")


@dp.message(F.text == "/help")
async def help_handler(msg: types.Message) -> None:
    help_text = (
        "🔮 <b>Зеркало Судьбы - Помощь</b>\n\n"
        "📋 <b>Доступные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/debug_hash - Отладка хеша (выводит в консоль полный процесс генерации)\n\n"
        "💳 <b>Оплата:</b>\n"
        "Оплата производится через Telegram Stars"
    )
    await msg.answer(help_text)


@dp.message(F.text.startswith("/debug_hash"))
async def debug_hash_handler(msg: types.Message) -> None:
    if not msg.from_user:
        return

    log.info("=== [БОТ] DEBUG HASH КОМАНДА ЗАПУЩЕНА ===")
    user = msg.from_user

    # Тестовые данные для поля 'user' - включаем ВСЕ потенциальные поля Telegram User.
    # Используем getattr с None по умолчанию, чтобы избежать AttributeError, если поля нет.
    user_data_dict = {
        "id": getattr(user, 'id', None),
        "is_bot": getattr(user, 'is_bot', None),
        "first_name": getattr(user, 'first_name', None),
        "last_name": getattr(user, 'last_name', None),
        "username": getattr(user, 'username', None),
        "language_code": getattr(user, 'language_code', None),
        "is_premium": getattr(user, 'is_premium', None),
        "added_to_attachment_menu": getattr(user, 'added_to_attachment_menu', None),
        "allows_write_to_pm": getattr(user, 'allows_write_to_pm', None),
        "photo_url": getattr(user, 'photo_url', None),
    }

    # Удаляем поля, которые имеют значение None.
    # Также удаляем булевы поля, если их значение False, НО это НЕ is_bot (is_bot:false может присутствовать).
    final_user_data_for_json = {}
    for k, v in user_data_dict.items():
        if v is None:
            continue
        # Если поле булево и оно False, и это не 'is_bot', то пропускаем его.
        # Telegram опускает false булевы поля в initData, кроме is_bot.
        if isinstance(v, bool) and v is False and k != 'is_bot':
            continue
        final_user_data_for_json[k] = v


    # ИСПРАВЛЕНИЕ: Вручную экранируем '/' на '\/' в photo_url, если Telegram так делает.
    if 'photo_url' in final_user_data_for_json and final_user_data_for_json['photo_url']:
        if '\\/' not in final_user_data_for_json['photo_url']:
            final_user_data_for_json['photo_url'] = final_user_data_for_json['photo_url'].replace('/', '\\/')
            log.info("[БОТ] photo_url экранирован для HMAC: %s", final_user_data_for_json['photo_url'])


    # Сериализуем dict в JSON-строку
    user_json_str = json.dumps(final_user_data_for_json, separators=(',', ':'), ensure_ascii=False)
    log.info("[БОТ] Сериализованная user_json_str (без URL-кодирования): %s", user_json_str)

    # URL-кодируем эту JSON-строку целиком, но не кодируем слеши (/)
    # quote(..., safe='/') соответствует поведению Telegram для URL внутри user-поля.
    user_value_for_init_data = quote(user_json_str, safe='/')
    log.info("[БОТ] URL-кодированная user_value_for_init_data: %s", user_value_for_init_data)

    # Теперь test_data_to_hash должен быть словарем, имитирующим парсинг initData
    test_data_to_hash = {
        "user": user_value_for_init_data,
        "auth_date": str(int(time.time())),
        "query_id": f"debug_{uuid.uuid4()}",
    }

    log.info("[БОТ] Данные для make_tg_hash (без 'hash'): %s", {k: v for k, v in test_data_to_hash.items() if k != 'hash'})


    # Создаем хеш с помощью make_tg_hash
    calculated_hash = make_tg_hash(test_data_to_hash.copy())
    test_data_to_hash["hash"] = calculated_hash

    # Формируем ответ пользователю
    response_text = (
        f"🔍 <b>Отладка хеша (результат в логах сервера)</b>\n\n"
        f"Для анализа откройте консоль, где запущен бот.\n\n"
        f"<b>Сгенерированный хешем:</b>\n<code>{calculated_hash}</code>\n\n"
        f"<b>Данные, которые использовались для генерации:</b>\n"
        f"<pre>{json.dumps(test_data_to_hash, indent=2, ensure_ascii=False)}</pre>"
    )

    await msg.answer(response_text)
    log.info("=== [БОТ] DEBUG HASH КОМАНДА ВЫПОЛНЕНА ===")


@dp.pre_checkout_query()
async def pre_checkout(pcq: types.PreCheckoutQuery) -> None:
    log.info("=== [БОТ] PRE-CHECKOUT QUERY ===")
    log.info("Пользователь: %s, Сумма: %s %s", pcq.from_user.id, pcq.total_amount, pcq.currency)

    if pcq.currency != "XTR":
        await bot.answer_pre_checkout_query(
            pcq.id, ok=False, error_message="Только Telegram Stars"
        )
        return

    await bot.answer_pre_checkout_query(pcq.id, ok=True)


@dp.message(F.successful_payment)
async def successful_payment(msg: types.Message) -> None:
    if not msg.successful_payment or not msg.from_user:
        return

    sp = msg.successful_payment
    log.info("=== [БОТ] УСПЕШНЫЙ ПЛАТЕЖ ===")
    log.info("Пользователь: %s, Сумма: %s %s", msg.from_user.id, sp.total_amount, sp.currency)

    webhook_data = {
        "message": {
            "successful_payment": {
                "currency": sp.currency,
                "total_amount": sp.total_amount,
                "invoice_payload": sp.invoice_payload,
                "telegram_payment_charge_id": sp.telegram_payment_charge_id,
                "provider_payment_charge_id": sp.provider_payment_charge_id,
            }
        },
        "user_id": msg.from_user.id,
        "username": msg.from_user.username or "",
        "timestamp": int(time.time()),
    }

    webhook_result = await make_api_request("/api/payments/webhook", webhook_data)
    if webhook_result is None:
        await msg.answer("⚠️ Платеж получен, но произошла ошибка при его обработке на сервере.")
    return

    await msg.answer(f"✅ <b>Платеж успешно обработан!</b>\n💰 Сумма: {sp.total_amount} {sp.currency}")


@dp.message()
async def unknown_message(msg: types.Message) -> None:
    await msg.answer("❓ Неизвестная команда. Используйте /help для получения помощи.")


async def main() -> None:
    log.info("=== [БОТ] ЗАПУСК ПОЛЛИНГА ===")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        log.critical("Критическая ошибка при запуске поллинга: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("=== [БОТ] ОСТАНОВЛЕН ВРУЧНУЮ ===")
    except Exception as e:
        log.critical("Критическая ошибка в main: %s", e, exc_info=True)
        sys.exit(1)
