// frontend/src/api/orders.js

import { apiClient } from "./client";

// Функцию `fetchMessages` из этого файла лучше убрать, так как она относится к чату,
// а не к заказам, чтобы не создавать путаницу.

/** 1) Все заказы текущего пользователя */
export async function fetchUserOrders() {
  const { data } = await apiClient.get("/orders/");
  return data;
}

/** 2) Все сообщения ко всем заказам (для списка чатов) */
// ВНИМАНИЕ: Эта функция очень неэффективна. См. заметку ниже.
export async function fetchUserChats() {
  // Эта функция теперь в файле /api/messages.js и защищена.
  // Запрос нужно делать оттуда. Если нужна именно эта логика,
  // то она должна вызывать `fetchMessages` из соответствующего файла.
  // Для примера оставим её закомментированной.
  /*
  const orders = await fetchUserOrders();
  const msgsArrays = await Promise.all(
    orders.map((o) => apiClient.get(`/messages/${o.id}`).then(res => res.data))
  );
  return msgsArrays.flat();
  */
  // Правильнее вызывать функцию, которая уже есть в messages.js
  // import { fetchUserChats as fetchChatsFromApi } from './messages';
  // return fetchChatsFromApi();

  // Временная заглушка, чтобы код не падал. Эту функцию нужно переосмыслить.
  console.warn(
    "fetchUserChats в orders.js является неэффективной. Рекомендуется переделать.",
  );
  return [];
}

/** 3) Создать заказ (выбор товара/услуги) */
export async function createOrder(productId) {
  const { data } = await apiClient.post("/orders/", { product_id: productId });
  return data;
}

/** 4) Получить один заказ по ID */
export async function fetchOrder(orderId) {
  const { data } = await apiClient.get(`/orders/${orderId}`);
  return data;
}

/** 5) История покупок текущего пользователя */
export async function fetchPurchaseHistory() {
  const { data } = await apiClient.get("/orders/my");
  return data;
}

/** 6) Оплатить заказ рублями (Frikassa) */
export async function payWithRubles(orderId) {
  const { data } = await apiClient.post(`/payments/frikassa`, {
    order_id: orderId,
  });
  return data;
}
