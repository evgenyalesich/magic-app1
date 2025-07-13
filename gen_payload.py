import time
import hmac
import hashlib
import json

# 1. Подставьте сюда свой BOT_TOKEN из .env
BOT_TOKEN = "7572912444:AAF2L7aLYt72UEb-uLqHDaSDOp2eldCPDrc"

# 2. Задайте любые тестовые значения
data = {
    "id": 6717031233,  # ваш telegram_id
    "username": "cpython99",  # username (необязательно)
    "auth_date": int(time.time()),  # текущее время
    # вы можете добавить другие поля, которые нужны вашему фронту:
    # "first_name": "Test",
    # "last_name": "User",
}

# 3. Вычисляем секретный ключ как sha256(BOT_TOKEN)
secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()

# 4. Формируем строку данных: "auth_date=…\nid=…\nusername=…" (в сортированном по имени ключей порядке)
data_check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

# 5. Считаем HMAC_SHA256 и кладём в поле hash
data["hash"] = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()

# 6. Выводим JSON
print(json.dumps(data, indent=2))
