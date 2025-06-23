// src/api/orders.js
import { fetchMessages } from "./messages";
const API_BASE = import.meta.env.VITE_API_URL || "";

/**
 * 1) Получить все заказы текущего пользователя
 *    GET /api/orders
 */
export async function fetchUserOrders() {
  const res = await fetch(`${API_BASE}/api/orders/`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Не удалось загрузить заказы");
  }
  return await res.json(); // массив OrderRead
}

/**
 * 2) Получить все сообщения по всем своим заказам
 *    для ChatListPage: возвращаем плоский массив MessageSchema
 */
export async function fetchUserChats() {
  const orders = await fetchUserOrders();
  // для каждого заказа загрузим все его сообщения
  const msgsArrays = await Promise.all(orders.map((o) => fetchMessages(o.id)));
  // объединяем в один массив
  return msgsArrays.flat();
}

/**
 * 3) Создать новый заказ (выбор услуги)
 *    POST /api/orders
 */
export async function createOrder(productId) {
  const res = await fetch(`${API_BASE}/api/orders/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ product_id: productId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Не удалось создать заказ");
  }
  return await res.json(); // { id, product, status, created_at }
}

/**
 * 4) Получить один заказ по ID
 *    GET /api/orders/{orderId}
 */
export async function fetchOrder(orderId) {
  const res = await fetch(`${API_BASE}/api/orders/${orderId}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Не удалось получить заказ");
  }
  return await res.json(); // OrderRead
}

/**
 * 5) Оплатить заказ «звёздами»
 *    POST /api/orders/{orderId}/pay-stars
 */
export async function payWithStars(orderId) {
  const res = await fetch(`${API_BASE}/api/orders/${orderId}/pay-stars`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Не удалось оплатить звёздами");
  }
  return await res.json(); // обновлённый OrderRead
}
