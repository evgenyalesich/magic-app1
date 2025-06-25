// frontend/src/api/messages.js
import { apiClient } from "./client";

/* ------------------------------------------------------------------
 * Вспомогательная функция: возвращаем res.data и пробрасываем ошибку
 * -----------------------------------------------------------------*/
function unwrap(res) {
  /*  apiClient (axios-обёртка) всегда отдаёт объект вида
      { data, status, … }.  Если HTTP-код ≥ 400, axios уже бросил
      исключение, поэтому здесь достаточно вернуть res.data. */
  return res.data;
}

/*───────────────── 1) список чатов пользователя ──────────────────────*/
/** GET /api/messages/ → [{ order_id, product, last_message, … }, …] */
export const fetchUserChats = () => apiClient.get("/messages/").then(unwrap);

/*───────────────── 2) полная переписка по заказу ─────────────────────*/
/** GET /api/messages/:id → [{ id, content, created_at, … }, …] */
export const fetchMessages = (orderId) =>
  apiClient.get(`/messages/${orderId}`).then(unwrap);

/*───────────────── 3) пользователь отправляет сообщение ──────────────*/
/** POST /api/messages/:id */
export const sendMessage = (orderId, content) => {
  const body = {
    order_id: orderId, // бэку удобно иметь ID и в body
    content,
    is_read: false, // новое сообщение помечаем непрочитанным
  };
  return apiClient.post(`/messages/${orderId}`, body).then(unwrap);
};

/*───────────────── 4) админ отвечает пользователю ────────────────────*/
/** POST /api/admin/messages/:id */
export const sendAdminMessage = (orderId, content) =>
  apiClient.post(`/admin/messages/${orderId}`, { content }).then(unwrap);

/*───────────────── 5) получить один заказ (для заголовков) ───────────*/
/** GET /api/orders/:id → { id, status, product: { title, … }, … } */
export const fetchOrder = (orderId) =>
  apiClient.get(`/orders/${orderId}`).then(unwrap);

/*───────────────── 6) последнее сообщение заказа (для списков) ───────*/
/** Берём только одну последнюю запись, если бэк это поддерживает.  */
export const fetchLastMessage = async (orderId) => {
  try {
    // Если у бэка есть параметры ?limit=1&direction=desc — используем их.
    const { data } = await apiClient.get(`/messages/${orderId}`, {
      params: { limit: 1, direction: "desc" },
    });
    return Array.isArray(data) ? (data.at(0) ?? null) : null;
  } catch {
    /* Фолбэк: грузим весь массив и берём последний элемент */
    const all = await fetchMessages(orderId);
    return Array.isArray(all) ? (all.at(-1) ?? null) : null;
  }
};
