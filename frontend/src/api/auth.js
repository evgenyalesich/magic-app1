import api from "./index";
import { useQuery } from "@tanstack/react-query";

/**
 * Логин через Telegram WebApp.
 */
export function loginWithTelegram(rawInitData) {
  console.group("📤 [auth.js] loginWithTelegram");
  console.log("  rawInitData:", rawInitData);
  console.log("  typeof rawInitData:", typeof rawInitData);
  console.log("  api base URL:", api.defaults.baseURL);

  return api
    .post("/auth/login", { init_data: rawInitData })
    .then((res) => {
      console.log("  ✅ [auth.js] /auth/login status:", res.status);
      console.log("  ✅ [auth.js] response headers:", res.headers);
      console.log("  ✅ [auth.js] response data:", res.data);
      console.groupEnd();
      return res.data;
    })
    .catch((err) => {
      console.error(
        "  ❌ [auth.js] /auth/login error status:",
        err.response?.status,
      );
      console.error(
        "  ❌ [auth.js] /auth/login error data:",
        err.response?.data,
      );
      console.error("  ❌ [auth.js] full error:", err);
      console.groupEnd();
      throw err;
    });
}

/**
 * Получение профиля текущего пользователя.
 */
export async function fetchMe() {
  console.group("👤 [auth.js] fetchMe");
  console.log("  api base URL:", api.defaults.baseURL);
  try {
    const { data, status, headers } = await api.get("/auth/me");
    console.log("  ✅ fetchMe status:", status);
    console.log("  ✅ fetchMe headers:", headers);
    console.log("  ✅ fetchMe data:", data);
    console.groupEnd();
    return data;
  } catch (err) {
    console.error("  ❌ fetchMe error status:", err.response?.status);
    console.error("  ❌ fetchMe error data:", err.response?.data);
    if (err.response?.status === 401) {
      console.warn("  ⚠️ fetchMe — not authorised (401)");
      console.groupEnd();
      return null;
    }
    console.groupEnd();
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
