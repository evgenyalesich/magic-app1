// импортируем общий axios-инстанс
import api from "./index";

// Получение “домашки” админки
export async function getAdminHome() {
  const { data } = await api.get("/admin");
  return data;
}

// Получение статистики админ-дашборда
export async function getAdminDashboard() {
  const { data } = await api.get("/admin/dashboard");
  return data;
}
