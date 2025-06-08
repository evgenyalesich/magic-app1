// frontend/src/telegram.js

const API_BASE = import.meta.env.VITE_API_BASE;
if (!API_BASE) {
  throw new Error("VITE_API_BASE не задан в окружении");
}

/**
 * Инициализирует Telegram WebApp, разворачивает его,
 * делает POST /api/auth/login(initDataUnsafe) и возвращает UserSchema.
 */
export async function initTelegram() {
  const tg = window.Telegram?.WebApp;
  if (!tg) {
    throw new Error("Этот код должен запускаться внутри Telegram WebApp");
  }
  tg.ready();
  tg.expand();

  const initData = tg.initDataUnsafe;
  if (!initData?.hash) {
    throw new Error("Нет initDataUnsafe.hash от Telegram");
  }

  // Шаг 1: логин (POST + set-cookie)
  const loginRes = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(initData),
  });
  if (!loginRes.ok) {
    const text = await loginRes.text();
    throw new Error(`Login failed: ${loginRes.status} ${text}`);
  }

  // Шаг 2: получить профиль
  const meRes = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: "include",
  });
  if (!meRes.ok) {
    const text = await meRes.text();
    throw new Error(`Fetch /me failed: ${meRes.status} ${text}`);
  }
  return meRes.json();
}

/**
 * Пробует прочитать /api/auth/me по кукам.
 */
export async function fetchCurrentUser() {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: "include",
  });
  if (!res.ok) return null;
  return res.json();
}
