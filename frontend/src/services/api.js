// Базовый URL вашего бэкенда (замените на свой домен)
const API_BASE_URL = 'https://full-resist-florist-faculty.trycloudflare.com';

// Утилита для запросов к API с обработкой ошибок и cookie
async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',           // передаём cookie для авторизации
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error ${res.status}: ${errorText}`);
  }
  return res.json();
}

// Службы API
export function fetchProducts() {
  return request('/api/products');
}

export function fetchProduct(id) {
  return request(`/api/products/${id}`);
}

export function createOrder(productId) {
  return request('/api/orders', {
    method: 'POST',
    body: JSON.stringify({ productId }),
  });
}

export function fetchChatHistory(sessionId) {
  return request(`/api/chat/${sessionId}/history`);
}

export function sendMessage(sessionId, message) {
  return request(`/api/chat/${sessionId}/message`, {
    method: 'POST',
    body: JSON.stringify(message),
  });
}