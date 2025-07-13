#!/bin/bash

# Выходим, если любая команда завершится с ошибкой
set -e

# --- Параметры ---
COMMIT_MSG="$1"
REMOTE_URL="$2"
BRANCH_NAME="$3"

# --- Проверки ---
if [ -z "$COMMIT_MSG" ]; then
    echo "Использование: $0 \"Сообщение\" [remote-URL] [имя-ветки]"
    echo "Пример 1 (пуш в текущую ветку):"
    echo "  $0 \"Исправил баг\""
    echo "Пример 2 (пуш в конкретную ветку):"
    echo "  $0 \"Новая фича\" \"\" \"feature-branch\"" # Пустой URL, если remote уже настроен
    exit 1
fi

# --- Логика ---

# 1) Инициализация, если нужно
if [ ! -d ".git" ]; then
    echo "[INFO] Git-репозиторий не найден. Инициализируем..."
    git init
fi

# 2) Настройка remote, если нужно
if ! git remote get-url origin > /dev/null 2>&1; then
    if [ -z "$REMOTE_URL" ]; then
        echo "Ошибка: удалённый репозиторий (origin) не настроен. Укажите URL."
        exit 1
    else
        echo "[INFO] Добавляем remote origin = $REMOTE_URL"
        git remote add origin "$REMOTE_URL"
    fi
fi

# 3) Определяем, в какую ветку пушить
# Если имя ветки не передано 3-м параметром, используем текущую
if [ -z "$BRANCH_NAME" ]; then
    BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
    echo "[INFO] Имя ветки не указано, используем текущую: $BRANCH_NAME"
fi

# 4) Добавляем, коммитим и пушим
echo "[INFO] git add ."
git add .

echo "[INFO] git commit -m \"$COMMIT_MSG\""
# Используем --allow-empty, чтобы избежать ошибки, если нет изменений для коммита
git commit -m "$COMMIT_MSG" --allow-empty || echo "[WARN] Нечего коммитить, но продолжаем пуш..."

echo "[INFO] git push -u origin $BRANCH_NAME"
git push -u origin "$BRANCH_NAME"

echo "[OK] Операция завершена успешно. Ветка '$BRANCH_NAME' отправлена на GitHub."
