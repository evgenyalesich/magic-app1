// frontend/src/services/api.js

export async function fetchProducts() {
  const res = await fetch('/api/products');
  if (!res.ok) throw new Error('Не удалось загрузить список товаров');
  return res.json();
}

export async function fetchProduct(id) {
  const res = await fetch(`/api/products/${id}`);
  if (!res.ok) throw new Error('Не удалось загрузить товар');
  return res.json();
}

export async function createOrder(productId) {
  const res = await fetch('/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ productId }),
  });
  if (!res.ok) throw new Error('Не удалось создать заказ');
  return res.json(); // { chatSessionId }
}

export async function fetchChatHistory(sessionId) {
  const res = await fetch(`/api/chat/${sessionId}/history`);
  if (!res.ok) throw new Error('Не удалось загрузить историю чата');
  return res.json(); // [{ sender, text, timestamp }, …]
}

export async function sendMessage(sessionId, message) {
  const res = await fetch(`/api/chat/${sessionId}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message),
  });
  if (!res.ok) throw new Error('Не удалось отправить сообщение');
  return res.json();
}
