// src/api/payments.js
const API_BASE = import.meta.env.VITE_API_URL || "";

async function postJson(path, payload = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  // читаем ответ как JSON, а если не вышло — как text
  let data;
  try {
    data = await res.json();
  } catch {
    data = await res.text();
  }

  if (!res.ok) {
    const msg = data?.detail || data?.message || data || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export const initPayment = (productId) =>
  postJson("/api/payments", { product_id: productId });
export const payWithStars = (orderId) =>
  postJson("/api/payments/stars", { order_id: orderId });
export const payWithFrikassa = (orderId) =>
  postJson("/api/payments/frikassa", { order_id: orderId });
