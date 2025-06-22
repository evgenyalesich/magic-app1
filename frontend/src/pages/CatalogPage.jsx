// src/pages/CatalogPage.jsx
import { useEffect, useState } from "react";
import { fetchProducts, createOrder } from "../api/products";
import styles from "./CatalogPage.module.css";

export default function CatalogPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [buyingId, setBuyingId] = useState(null);

  useEffect(() => {
    async function loadProducts() {
      try {
        const products = await fetchProducts();
        setItems(products);
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить товары");
      } finally {
        setLoading(false);
      }
    }

    loadProducts();
  }, []);

  const handleBuy = async (id) => {
    setBuyingId(id);
    try {
      await createOrder(id);
      // Можно заменить alert на более «нативный» тост
      alert("Заказ оформлен");
    } catch {
      alert("Ошибка при оформлении заказа");
    } finally {
      setBuyingId(null);
    }
  };

  if (loading) {
    return <div className={styles.placeholder}>Загрузка…</div>;
  }

  if (error) {
    return <div className={styles.placeholder}>{error}</div>;
  }

  if (items.length === 0) {
    return <div className={styles.placeholder}>Товаров пока нет</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.grid}>
        {items.map((item) => (
          <div key={item.id} className={styles.card}>
            <img
              src={item.image_url}
              alt={item.title}
              className={styles.cardImage}
            />
            <div className={styles.cardContent}>
              <h2 className={styles.title}>{item.title}</h2>
              <p className={styles.description}>{item.description}</p>
              <div className={styles.footer}>
                <span className={styles.price}>{item.price} ₽</span>
                <button
                  className={styles.button}
                  disabled={buyingId === item.id}
                  onClick={() => handleBuy(item.id)}
                >
                  {buyingId === item.id ? "Оформление…" : "Купить"}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
