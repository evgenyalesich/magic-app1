// frontend/src/api/messages.js
import { apiClient } from "./client";

// 1) Список чатов
export async function fetchUserChats() {
  const { data } = await apiClient.get("/messages");
  return data;
}

// 2) История переписки
export async function fetchMessages(orderId) {
  const { data } = await apiClient.get(`/messages/${orderId}`);
  return data;
}

// 3) Отправить сообщение
export async function sendMessage(orderId, content) {
  const { data } = await apiClient.post(`/messages/${orderId}`, {
    order_id: orderId, // добавить это
    content,
    is_read: false, // добавить это
  });
  return data;
}
// 4) Админская отправка
export async function sendAdminMessage(orderId, content) {
  const { data } = await apiClient.post(`/admin/messages/${orderId}`, {
    content,
  });
  return data;
}
