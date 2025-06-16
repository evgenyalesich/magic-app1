// src/api/auth.js
import api from "./index";
import { useQuery } from "@tanstack/react-query";

/**
 * Логин через Telegram WebApp.
 * @param {string} rawInitData — неизменённая строка вида "k1=v1&…&hash=…"
 * @returns {Promise<any>}
 */
export function loginWithTelegram(rawInitData) {
  return api
    .post("/auth/login", { init_data: rawInitData })
    .then((res) => res.data);
}

/**
 * Получение профиля текущего пользователя.
 * При 401 возвращает null.
 */
export async function fetchMe() {
  try {
    const { data } = await api.get("/auth/me");
    return data;
  } catch (err) {
    if (err.response?.status === 401) {
      return null;
    }
    throw err;
  }
}

/**
 * Хук react-query для /auth/me
 */
export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
    retry: false,
    refetchOnWindowFocus: false,
    staleTime: 60_000,
  });
}
