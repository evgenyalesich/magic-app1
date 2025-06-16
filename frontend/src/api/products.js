// frontend/src/api/products.js
import api from "./index"; // ваш axios instance с baseURL=/api, withCredentials и т.д.

// получить список
export function fetchProducts() {
  return api.get("/products").then((res) => res.data);
}

// сделать заказ
export function createOrder(productId) {
  return api.post("/orders", { product_id: productId }).then((res) => res.data);
}

// —————————————
// добавляем создание товара (админка)
// —————————————
export function createProduct(product) {
  // product: { name, description, price, image }
  return api.post("/products", product).then((res) => res.data);
}
