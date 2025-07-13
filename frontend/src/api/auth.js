// src/services/auth.js

import axios from "axios";
import { useQuery } from "@tanstack/react-query";

// ───────────────────────────────────────────────────────────────────────────
// 0. Axios instance
// ───────────────────────────────────────────────────────────────────────────
// Укажите VITE_API_BASE_URL в .env.[mode]  (например, https://api.example.com)
// В dev‑режиме по умолчанию проксируется на "/api".
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
});

// ───────────────────────────────────────────────────────────────────────────
// 1. Работа с initData (storage helpers)
// ───────────────────────────────────────────────────────────────────────────
const INIT_KEY = "tg_init_data"; // sessionStorage, живёт пока открыта вкладка

export function getInitData() {
  return sessionStorage.getItem(INIT_KEY);
}

export function setInitData(raw) {
  sessionStorage.setItem(INIT_KEY, raw);
}

export function clearInitData() {
  sessionStorage.removeItem(INIT_KEY);
}

// ───────────────────────────────────────────────────────────────────────────
// 2. Axios interceptors
// ───────────────────────────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const init = getInitData();
    if (init) config.headers["X-Telegram-Init-Data"] = init;
    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // invalid / expired initData ⇒ чистим storage, чтобы React‑Query перезапросил /me
      clearInitData();
    }
    return Promise.reject(error);
  },
);

// ───────────────────────────────────────────────────────────────────────────
// 3. Auth API helpers
// ───────────────────────────────────────────────────────────────────────────
/**
 * Логин через Telegram Web App.
 * Отправляем `initData` => получаем данные пользователя.
 * @param {string} initData – строка Telegram.WebApp.initData (raw)
 * @returns {Promise<object>} user
 */
export async function loginWithTelegram(initData) {
  const { data } = await api.post("/auth/login", { init_data: initData });
  setInitData(initData); // сохраняем до закрытия вкладки
  return data.user; // backend возвращает { user: { … } }
}

/**
 * Выход из приложения – на сервер ходить не нужно, достаточно забыть initData.
 */
export function logout() {
  clearInitData();
}

/**
 * Current user (однократный вызов – кешируется React‑Query)
 */
export async function fetchMe() {
  const { data } = await api.get("/auth/me");
  return data; // backend отдаёт UserSchema
}

/**
 * React‑hook, который автоматически делает /me, если есть initData.
 */
export function useMe() {
  const enabled = Boolean(getInitData());
  return useQuery({ queryKey: ["me"], queryFn: fetchMe, enabled });
}

// ───────────────────────────────────────────────────────────────────────────
// 4. Utils
// ───────────────────────────────────────────────────────────────────────────
export function isAuthenticated() {
  return Boolean(getInitData());
}

// Default export для остальных сервисов (при необходимости)
export default api;
