// src/api/chat.js
import { apiClient } from "./client";
/**
 * Собирает URL для истории или long-poll.
 */
function makeUrl(orderId, since = "", usePoll = false) {
  if (usePoll) {
    const qs = since ? `?after=${encodeURIComponent(since)}` : "";
    return `/messages/${orderId}/poll${qs}`;
  }
  if (since) {
    return `/messages/${orderId}?since=${encodeURIComponent(since)}`;
  }
  return `/messages/${orderId}`;
}

/**
 * Получить историю / новые сообщения.
 * @param {number|string} orderId
 * @param {string} since     пустая строка → вся история, иначе только после since
 * @param {boolean} usePoll  true → /poll-эндпоинт
 * @param {AbortSignal} [signal] опционально, для отмены long-poll
 * @returns {Promise<Array>} список MessageOut
 */
export function fetchMessages(orderId, since = "", usePoll = false, signal) {
  const url = makeUrl(orderId, since, usePoll);
  return apiClient.get(url, { signal }).then((res) => res.data);
}

/**
 * Отправить новое сообщение.
 * @param {number|string} orderId
 * @param {string} content
 * @param {string} [client_tmp_id] временный id для optimistic UI
 * @returns {Promise<Object>} отправленное сообщение
 */
export function sendMessage(orderId, content, client_tmp_id) {
  const body = { content };
  if (client_tmp_id) body.client_tmp_id = client_tmp_id;
  return apiClient.post(`/messages/${orderId}`, body).then((res) => res.data);
}
