// File: frontend/src/telegram.js

const API_BASE = import.meta.env.VITE_API_BASE
if (!API_BASE) {
  throw new Error("VITE_API_BASE не задан в .env")
}

export async function initTelegram() {
  const tg = window.Telegram?.WebApp
  if (!tg) {
    throw new Error("Этот код должен запускаться внутри Telegram WebApp")
  }
  tg.ready()
  tg.expand()

  const initData = tg.initDataUnsafe
  if (!initData?.hash) {
    throw new Error("Не удалось получить hash из initDataUnsafe")
  }

  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(initData),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Login failed: ${res.status} ${text}`)
  }
  return res.json()
}

export async function fetchCurrentUser() {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: "include",
  })
  if (!res.ok) {
    return null
  }
  return res.json()
}
