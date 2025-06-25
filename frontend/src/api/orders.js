// src/api/orders.js
import { fetchMessages } from "./messages";

const API_BASE = import.meta.env.VITE_API_URL || "";

/*────────────────── helpers ──────────────────*/
async function getJson(url) {
  const res = await fetch(url, { credentials: "include" });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Ошибка запроса");
  return data;
}

async function postJson(url, payload = {}) {
  const res = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Ошибка запроса");
  return data;
}

/*────────────────── API ──────────────────*/

/** 1) Все заказы текущего пользователя */
export const fetchUserOrders = () => getJson(`${API_BASE}/api/orders/`);

/** 2) Все сообщения ко всем заказам (для списка чатов) */
export async function fetchUserChats() {
  const orders = await fetchUserOrders();
  const msgsArrays = await Promise.all(orders.map((o) => fetchMessages(o.id)));
  return msgsArrays.flat();
}

/** 3) Создать заказ (выбор товара/услуги) */
export const createOrder = (productId) =>
  postJson(`${API_BASE}/api/orders/`, { product_id: productId });

/** 4) Получить один заказ по ID */
export const fetchOrder = (orderId) =>
  getJson(`${API_BASE}/api/orders/${orderId}`);

/** 5) Оплатить заказ Рублями (Frikassa).
 *    backend вернёт `{ payment_url }` для перенаправления пользователя. */
export const payWithRubles = (orderId) =>
  postJson(`${API_BASE}/api/payments/frikassa`, { order_id: orderId });

/* payWithStars удалён: реальное списание звёзд идёт через Telegram-invoice */
