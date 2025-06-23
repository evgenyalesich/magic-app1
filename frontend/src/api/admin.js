// src/api/admin.js
import api from "./index";

/**
 * Общий обработчик ошибок axios:
 * — Если сервер вернул JSON с полем detail или message, бросаем его;
 * — Иначе пробрасываем исходную ошибку.
 */
function handleApiError(err) {
  if (err.response && err.response.data) {
    const { detail, message } = err.response.data;
    throw new Error(detail || message || `Ошибка ${err.response.status}`);
  }
  throw err;
}

/* ---------- Админ-панель ---------- */

export const getAdminHome = async () => {
  try {
    const { data } = await api.get("/admin");
    return data;
  } catch (err) {
    handleApiError(err);
  }
};

export const getAdminDashboard = async () => {
  try {
    const { data } = await api.get("/admin/dashboard");
    return data;
  } catch (err) {
    handleApiError(err);
  }
};

/* ---------- CRUD товаров ---------- */

export const fetchAdminProducts = async () => {
  try {
    const { data } = await api.get("/admin/products");
    return data;
  } catch (err) {
    handleApiError(err);
  }
};

export const createAdminProduct = async (payload) => {
  try {
    const { data } = await api.post("/admin/products", payload);
    return data;
  } catch (err) {
    handleApiError(err);
  }
};

export const updateAdminProduct = async (id, payload) => {
  try {
    const { data } = await api.put(`/admin/products/${id}`, payload);
    return data;
  } catch (err) {
    handleApiError(err);
  }
};

export const deleteAdminProduct = async (id) => {
  try {
    const { data } = await api.delete(`/admin/products/${id}`);
    return data;
  } catch (err) {
    handleApiError(err);
  }
};

/* ---------- Сообщения админа ---------- */

/**
 * Подгружает СРАЗУ все сообщения со всех заказов (Pydantic-схема AdminMessageWithExtras).
 */
export const fetchAdminMessages = async () => {
  try {
    const { data } = await api.get("/admin/messages/");
    return data; // [ { id, order_id, content, reply, is_read, created_at, replied_at, user_name, product_title }, ... ]
  } catch (err) {
    handleApiError(err);
  }
};

/**
 * Список чатов: группировка по order_id + самое свежее сообщение из каждого.
 */

export const fetchAdminChats = async () => {
  const msgs = await fetchAdminMessages(); // [{ order_id, product_title, created_at, ... }, ...]
  const byOrder = {}; // { [orderId]: { order_id, product: {title}, last_message } }

  msgs.forEach((m) => {
    const key = String(m.order_id);
    const prev = byOrder[key];

    // если чат ещё не заведен или текущее сообщение новее предыдущего — перезаписываем
    if (
      !prev ||
      new Date(prev.last_message.created_at) < new Date(m.created_at)
    ) {
      byOrder[key] = {
        order_id: m.order_id,
        product: { title: m.product_title },
        last_message: m,
      };
    }
  });

  return Object.values(byOrder);
};
/**
 * История переписки по одному заказу — просто фильтруем уже загруженный набор.
 */
export const fetchAdminChat = async (orderId) => {
  const msgs = await fetchAdminMessages();
  return msgs.filter((m) => String(m.order_id) === String(orderId));
};

/**
 * Отправить новое сообщение админом в конкретный заказ.
 */
export const sendAdminMessage = async (orderId, content) => {
  try {
    const { data } = await api.post(`/admin/messages/${orderId}`, { content });
    return data; // возвращается единичное MessageSchema
  } catch (err) {
    handleApiError(err);
  }
};

/* ---------- Отчёты ---------- */

export const fetchAdminReport = async () => {
  try {
    const { data } = await api.get("/admin/report");
    return data;
  } catch (err) {
    handleApiError(err);
  }
};
