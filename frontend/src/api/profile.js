// src/api/profile.js

// Предполагается, что ваш настроенный axios-клиент находится здесь
import { apiClient } from "./client";

export async function getProfile() {
  // Используем apiClient, который автоматически добавит заголовок авторизации
  const { data } = await apiClient.get("/profile"); // Путь уже включает /api
  return data;
}
