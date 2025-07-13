import { apiClient } from "./client";

const unwrap = (res) => res.data;

/* --------------------------------------------------------------
 * URL-builder
 * ------------------------------------------------------------- */
function makeChatUrl(orderId, since = "", usePoll = false) {
  if (usePoll) {
    // long-poll энд-пойнт
    const qs = since ? `?after=${encodeURIComponent(since)}` : "";
    return `/messages/${orderId}/poll${qs}`;
  }
  // обычный one-shot запрос
  if (since) {
    return `/messages/${orderId}?since=${encodeURIComponent(since)}`;
  }
  return `/messages/${orderId}`;
}

/* ==============================================================
 *                         PUBLIC  API
 * ============================================================== */
/**
 * Список чатов (по одному последнему сообщению в заказе)
 */
export const fetchUserChats = () => apiClient.get("/messages/").then(unwrap);

/**
 * Получить историю / новые сообщения.
 * @param {number|string}  orderId
 * @param {string}  [since]      ISO-метка последнего сообщения
 * @param {boolean} [usePoll]    true → long-poll энд-пойнт
 * @param {AbortSignal} [signal] для прерывания висящего fetch
 */
export async function fetchMessages(
  orderId,
  since = "",
  usePoll = false,
  signal = undefined,
) {
  const url = makeChatUrl(orderId, since, usePoll);
  return (await apiClient.get(url, { signal })).data;
}

/**
 * Отправить сообщение от пользователя.
 * tmpId (client_tmp_id) опционален — нужен для optimistic-UI.
 */
export function sendMessage(orderId, content, tmpId) {
  const body = {
    order_id: orderId,
    content,
    ...(tmpId && { client_tmp_id: tmpId }),
  };
  return apiClient.post(`/messages/${orderId}`, body).then(unwrap);
}

/* --------------------------------------------------------------
 * Админские helper-ы (оставлены, потому что фронт ими пользуется)
 * ------------------------------------------------------------- */
export const sendAdminMessage = (orderId, content, tmpId) =>
  apiClient
    .post(`/admin/messages/${orderId}`, {
      content,
      ...(tmpId && { client_tmp_id: tmpId }),
    })
    .then(unwrap);

/* --------------------------------------------------------------
 * Заказ и помощники
 * ------------------------------------------------------------- */
export const fetchOrder = (orderId) =>
  apiClient.get(`/orders/${orderId}`).then(unwrap);

export const fetchLastMessage = async (orderId) => {
  try {
    const { data } = await apiClient.get(`/messages/${orderId}`, {
      params: { limit: 1, direction: "desc" },
    });
    return Array.isArray(data) ? (data[0] ?? null) : null;
  } catch {
    const all = await fetchMessages(orderId);
    return Array.isArray(all) ? (all.at(-1) ?? null) : null;
  }
};
