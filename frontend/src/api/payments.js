// src/api/payments.js
const API_BASE = import.meta.env.VITE_API_URL || "";

/* helper ------------------------------------------------------------------ */
async function postJson(path, payload = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  // пробуем json → иначе text
  let data;
  try {
    data = await res.json();
  } catch {
    data = await res.text();
  }

  if (!res.ok) {
    throw new Error(
      data?.detail || data?.message || data || `HTTP ${res.status}`,
    );
  }
  return data;
}

/* public ------------------------------------------------------------------ */
export const initPayment = (productId, quantity = 1) =>
  postJson("/api/payments", { product_id: productId, quantity });

export const payWithFrikassa = (orderId) =>
  postJson("/api/payments/frikassa", { order_id: orderId });
