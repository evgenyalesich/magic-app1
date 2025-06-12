export async function fetchProducts() {
  const res = await fetch('/api/products')
  if (!res.ok) throw new Error('Cannot load products')
  return res.json()
}

export async function createOrder(productId) {
  const res = await fetch('/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  })
  if (!res.ok) throw new Error('Order failed')
  return res.json()
}
