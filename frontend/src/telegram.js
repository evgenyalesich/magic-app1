// frontend/src/telegram.js

const API_BASE = process.env.REACT_APP_API_BASE;
if (!API_BASE) {
  throw new Error('REACT_APP_API_BASE не задан в .env');
}

/**
 * Инициализирует Telegram Web App, разворачивает его на весь экран,
 * отправляет initDataUnsafe на бэкенд для верификации и возвращает профиль пользователя.
 */
export async function initTelegram() {
  const tg = window.Telegram?.WebApp;
  if (!tg) {
    throw new Error('Этот код должен выполняться внутри Telegram WebApp');
  }

  // Telegram WebApp готов к работе
  tg.ready();
  // Разворачивание на весь экран
  tg.expand();

  // У Telegram WebApp есть два набора данных:
  // - initData (закодированная строка)
  // - initDataUnsafe (распарсенный объект, но без проверки)
  const initData = tg.initDataUnsafe;
  if (!initData || !initData.hash) {
    throw new Error('Не удалось получить валидные initData от Telegram');
  }

  // Шаг 1: передаём на бэкенд, проверяем hash и ставим куки
  const loginRes = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(initData),
  });
  if (!loginRes.ok) {
    const text = await loginRes.text();
    throw new Error(`Login failed: ${loginRes.status} ${text}`);
  }

  // Шаг 2: после успешного логина сразу тащим профиль
  const meRes = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: 'include',
  });
  if (!meRes.ok) {
    throw new Error(`Не удалось получить профиль: ${meRes.status}`);
  }

  return meRes.json();
}

/**
 * Если WebApp не доступен (например, запустили просто в браузере),
 * попытаемся взять пользователя по уже установленным кукам.
 */
export async function fetchCurrentUser() {
  const meRes = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: 'include',
  });
  if (!meRes.ok) {
    return null;
  }
  return meRes.json();
}
