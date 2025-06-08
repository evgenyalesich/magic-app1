// File: frontend/src/telegram.js

// Базовый URL вашего бэкенда
const API_BASE = process.env.REACT_APP_API_BASE || '';

/**
 * Инициализирует Telegram Web App, расширяет окно на весь экран,
 * верифицирует initData на сервере и возвращает профиль пользователя.
 */
export async function initTelegram() {
  const tg = window.Telegram?.WebApp;
  if (!tg) {
    throw new Error('Запущено не из Telegram WebApp');
  }

  tg.ready();
  tg.expand();

  // Telegram кладёт все данные при запусе веб-приложения
  const payload = tg.initDataUnsafe;
  if (!payload || !payload.hash) {
    throw new Error('Нет initData или hash от Telegram');
  }

  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',         // обязательно, чтобы сохранить куки
    body: JSON.stringify(payload), // передаём весь объект с hash/auth_date/…
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Login failed: ${res.status} ${text}`);
  }

  return res.json(); // { telegram_id, username, … }
}
