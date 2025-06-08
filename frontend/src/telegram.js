// frontend/src/telegram.js
const API_BASE = import.meta.env.VITE_API_BASE;
if (!API_BASE) {
  throw new Error("VITE_API_BASE не задан в .env");
}

/**
 * Инициализируем Telegram WebApp и логинимся на бэке
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
    throw new Error("Не получил initDataUnsafe.hash от Telegram");
  }

  // POST /api/auth/login → ставит куки
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
  return loginRes.json();
}

/**
 * GET /api/auth/me по кукам
 */
export async function fetchCurrentUser() {
  const meRes = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: "include",
  });
  if (!meRes.ok) return null;
  return meRes.json();
}
