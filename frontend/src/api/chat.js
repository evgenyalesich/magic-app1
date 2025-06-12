// frontend/src/api/chat.js

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Подгружает историю сообщений для конкретного заказа.
 * @param {number|string} orderId
 * @returns {Promise<Array>} массив сообщений
 */
export async function fetchMessages(orderId) {
  const res = await fetch(`${API_BASE}/messages?order_id=${orderId}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Не удалось получить сообщения: ${text}`);
  }
  return res.json();
}

/**
 * Отправляет новое сообщение в чат по заказу.
 * @param {number|string} orderId
 * @param {string} content — текст сообщения
 * @returns {Promise<Object>} вновь созданное сообщение
 */
export async function sendMessage(orderId, content) {
  const payload = { order_id: orderId, content };
  const res = await fetch(`${API_BASE}/messages`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Не удалось отправить сообщение: ${text}`);
  }
  return res.json();
}
