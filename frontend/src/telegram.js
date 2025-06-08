// File: frontend/src/telegram.js
const API_BASE = process.env.REACT_APP_API_BASE; // или как вы у себя храните базовый URL

export async function initTelegram() {
  const tg = window.Telegram.WebApp;
  tg.expand();

  if (!tg.initDataUnsafe) {
    throw new Error('Telegram WebApp не инициализирован');
  }

  // 1) логинимся
  const loginRes = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    credentials: 'include',           // ← чтобы браузер сохранил и прислал куки
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tg.initDataUnsafe),
  });
  if (!loginRes.ok) {
    throw new Error('Login failed');
  }
  const me = await loginRes.json();

  // 2) теперь, если нужно, проверяем /api/auth/me
  const meRes = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: 'include',
  });
  if (!meRes.ok) {
    throw new Error('Не удалось получить профиль');
  }
  return meRes.json();
}
