// src/api/admin.js
import api from "./index";

/* ---------- Админ-панель ---------- */

// Домашний экран (приветственный текст, версии и т.д.)
export const getAdminHome = async () => {
  const { data } = await api.get("/admin");
  return data;
};

// Общая статистика / метрики дашборда
export const getAdminDashboard = async () => {
  const { data } = await api.get("/admin/dashboard");
  return data;
};

/* ---------- CRUD товаров для админа ---------- */

// Список всех товаров
export const fetchAdminProducts = async () => {
  const { data } = await api.get("/admin/products");
  return data;
};

// Добавить новый товар
export const createAdminProduct = async (payload) => {
  const { data } = await api.post("/admin/products", payload);
  return data;
};

// Обновить существующий товар
export const updateAdminProduct = async (id, payload) => {
  const { data } = await api.put(`/admin/products/${id}`, payload);
  return data;
};

// Удалить товар
export const deleteAdminProduct = async (id) => {
  await api.delete(`/admin/products/${id}`);
};

/* ---------- Сообщения админа ---------- */

// Список всех сообщений
export const fetchAdminMessages = async () => {
  const { data } = await api.get("/admin/messages");
  return data;
};

// Удалить сообщение по ID
export const deleteAdminMessage = async (id) => {
  await api.delete(`/admin/messages/${id}`);
};

/* ---------- Отчёт / Статистика ---------- */

// Получить данные отчёта
export const fetchAdminReport = async () => {
  const { data } = await api.get("/admin/report");
  return data;
};
