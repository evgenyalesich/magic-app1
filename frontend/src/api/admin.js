import { apiClient } from "./client";

function unwrap(res) {
  return res.data;
}

/* ── PRODUCTS ─────────────────────────────────────────────────────────── */

export const fetchAdminProducts = () =>
  apiClient.get("/admin/products").then(unwrap);

export const createAdminProduct = (data) =>
  apiClient.post("/admin/products", data).then(unwrap);

export const updateAdminProduct = (id, data) =>
  apiClient.put(`/admin/products/${id}`, data).then(unwrap);

export const deleteAdminProduct = (id) =>
  apiClient.delete(`/admin/products/${id}`).then(unwrap);

/* ── CHATS & MESSAGES ───────────────────────────────────────────────── */
export const fetchAdminChats = () =>
  apiClient.get("/admin/messages/").then(unwrap);

export const fetchAdminMessages = (orderId) =>
  apiClient.get(`/admin/messages/${orderId}`).then(unwrap);

export const sendAdminMessage = (orderId, content) =>
  apiClient.post(`/admin/messages/${orderId}`, { content }).then(unwrap);

export const deleteAdminMessage = (messageId) =>
  apiClient.delete(`/admin/messages/single/${messageId}`).then(() => null);

export const deleteAdminChat = (orderId) =>
  apiClient.delete(`/admin/messages/${orderId}`).then(() => null);

/* ── REPORT ──────────────────────────────────────────────────────────── */

export const fetchAdminReport = () =>
  apiClient.get("/admin/report/").then(unwrap);

/* ── ORDERS & HELPERS ────────────────────────────────────────────────── */

export const fetchOrder = (orderId) =>
  apiClient.get(`/orders/${orderId}`).then(unwrap);

export const fetchLastMessage = async (orderId) => {
  try {
    const { data } = await apiClient.get(`/admin/messages/${orderId}`, {
      params: { limit: 1, direction: "desc" },
    });
    return Array.isArray(data) ? (data[0] ?? null) : null;
  } catch {
    const all = await fetchAdminMessages(orderId);
    return Array.isArray(all) ? (all.at(-1) ?? null) : null;
  }
};
