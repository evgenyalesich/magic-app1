// File: frontend/src/telegram.js

/**
 * Инициализирует Telegram Web App, расширяет окно и
 * верифицирует initData на сервере, получая профиль пользователя.
 */
export async function initTelegram() {
  const tg = window.Telegram.WebApp;

  // Разворачиваем Web App на весь экран
  tg.expand();

  // Проверяем, что API доступен
  if (!tg.initData) {
    throw new Error('Telegram WebApp не инициализирован');
  }

  // Отправляем initData на сервер для верификации и получения пользователя
  const res = await fetch('/api/verify_initdata', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ initData: tg.initData }),
  });
  if (!res.ok) {
    throw new Error('Не удалось верифицировать initData');
  }
  return res.json(); // { telegram_id, name, username, … }
}
