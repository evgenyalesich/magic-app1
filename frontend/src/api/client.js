// src/api/client.js  <-- Рекомендуемое имя файла

import axios from "axios";

// Функции для работы с initData. Их можно оставить в auth.js и импортировать,
// но держать здесь надёжнее, чтобы избежать циклических зависимостей.
function getInitData() {
  return sessionStorage.getItem("tg_init_data");
}
function clearInitData() {
  sessionStorage.removeItem("tg_init_data");
}

// Создаём и экспортируем единый клиент
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

// --- Сразу настраиваем перехватчики ---

// Перехватчик ЗАПРОСА: добавляет заголовок авторизации
apiClient.interceptors.request.use(
  (config) => {
    const initData = getInitData();
    if (initData) {
      config.headers["X-Telegram-Init-Data"] = initData;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Перехватчик ОТВЕТА: обрабатывает ошибки 401 (не авторизован)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Если сервер ответил 401, значит, наши данные невалидны.
      // Чистим их, чтобы "разлогинить" пользователя.
      clearInitData();
      // Опционально: можно перезагрузить страницу, чтобы пользователь попал на логин
      // window.location.reload();
    }
    return Promise.reject(error);
  },
);

// Этот экспорт можно убрать, чтобы избежать путаницы.
// Используйте везде именованный импорт: import { apiClient } from '...'
// export default apiClient;
