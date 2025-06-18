// src/api/telegramAuth.js

const API_BASE = import.meta.env.VITE_API_BASE;
if (!API_BASE) {
  throw new Error("VITE_API_BASE не задан в .env");
}

/**
 * Проверяет, есть ли действующая сессия (tg_id-cookie)
 * и возвращает профиль пользователя.
 * Бросает ошибку, если не авторизован.
 */
export async function loginViaSession() {
  console.group("[telegramAuth] loginViaSession");
  console.log("  → GET /api/auth/me");
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: "include",
  });
  console.log("  ← status", res.status);
  if (!res.ok) {
    console.error("  ❌ Not authenticated, status", res.status);
    console.groupEnd();
    throw new Error(
      "Не авторизован. Откройте этот мини-приложение из вашего Telegram-бота.",
    );
  }
  const user = await res.json();
  console.log("  ✅ Authenticated user:", user);
  console.groupEnd();
  return user;
}

/**
 * Фоллбэк на случай, если нужна просто проверка сессии
 * без ошибок (возвращает null вместо броска).
 */
export async function fetchCurrentUser() {
  console.group("[telegramAuth] fetchCurrentUser");
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: "include",
  });
  console.log("  ← status", res.status);
  if (!res.ok) {
    console.warn("  ⚠️ Not authenticated, returning null");
    console.groupEnd();
    return null;
  }
  const user = await res.json();
  console.log("  ✅ User:", user);
  console.groupEnd();
  return user;
}
