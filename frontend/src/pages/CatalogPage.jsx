// src/pages/CatalogPage.jsx
import { useEffect, useState } from "react";
import { fetchProducts, createOrder } from "../api/products";
import styles from "./CatalogPage.module.css";

export default function CatalogPage() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetchProducts().then(setItems);
  }, []);

  const handleBuy = async (id) => {
    await createOrder(id);
    alert("Заказ оформлен");
  };

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
                  onClick={() => handleBuy(item.id)}
                >
                  Купить
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
