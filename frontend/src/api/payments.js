// src/api/payments.js
import { apiClient } from "./client"; // Используем общий клиент

/**
 * Отправляет POST-запрос
 */
async function postJson(path, payload = {}) {
  const { data } = await apiClient.post(path, payload);
  return data;
}

/**
 * Создать новый pending-заказ (количество всегда = 1)
 * и получить invoice-ссылку для оплаты звёздами.
 */
export function createOrderForStars(productId) {
  return postJson("/payments/", { product_id: productId });
}

/**
 * ✅ ВОССТАНОВЛЕННАЯ ФУНКЦИЯ
 * Получить invoice-ссылку для уже существующего pending-заказа.
 */
export function getStarsInvoice(orderId) {
  return postJson(`/payments/${orderId}/stars`);
}

/**
 * Получить ссылку на оплату через Frikassa для существующего заказа.
 */
export function payWithFrikassa(orderId) {
  return postJson("/payments/frikassa", { order_id: orderId });
}
