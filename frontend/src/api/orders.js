const API_BASE = import.meta.env.VITE_API_URL || '';

export async function createOrder(productId) {
  const res = await fetch(`${API_BASE}/api/orders`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  });
  if (!res.ok) throw new Error('Order creation failed');
  return await res.json(); // { id, product: {...}, status, created_at }
}

export async function fetchOrder(orderId) {
  const res = await fetch(`${API_BASE}/api/orders/${orderId}`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Could not fetch order');
  return await res.json();
}
