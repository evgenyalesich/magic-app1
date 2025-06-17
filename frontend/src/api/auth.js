import api from "./index";
import { useQuery } from "@tanstack/react-query";

/**
 * Логин через Telegram WebApp.
 * @param {string} rawInitData — неизменённая строка вида "k1=v1&…&hash=…"
 * @returns {Promise<any>}
 */
export function loginWithTelegram(rawInitData) {
  console.log("📤 [auth.js] Отправка init_data в login:", rawInitData); // 👈 LOG

  return api
    .post("/auth/login", { init_data: rawInitData })
    .then((res) => {
      console.log("✅ [auth.js] Ответ login:", res.data); // 👈 LOG
      return res.data;
    })
    .catch((err) => {
      console.error("❌ [auth.js] Ошибка login:", err?.response?.data || err); // 👈 LOG
      throw err;
    });
}

/**
 * Получение профиля текущего пользователя.
 * При 401 возвращает null.
 */
export async function fetchMe() {
  try {
    const { data } = await api.get("/auth/me");
    console.log("👤 [auth.js] fetchMe — профиль:", data); // 👈 LOG
    return data;
  } catch (err) {
    if (err.response?.status === 401) {
      console.warn("⚠️ [auth.js] fetchMe — не авторизован"); // 👈 LOG
      return null;
    }
    console.error("❌ [auth.js] fetchMe — ошибка:", err?.response?.data || err); // 👈 LOG
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
