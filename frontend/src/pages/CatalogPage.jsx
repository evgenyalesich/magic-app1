// src/pages/CatalogPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// 1. Импортируем хук useMe
import { useMe } from "../api/auth";
import { fetchProducts } from "../api/products";
import styles from "./CatalogPage.module.css";

export default function CatalogPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const navigate = useNavigate();

  // 2. Получаем статус загрузки пользователя
  const { isSuccess: isUserLoaded, isLoading: isUserLoading } = useMe();

  useEffect(() => {
    // 3. Запускаем запрос, только если пользователь авторизован
    if (isUserLoaded) {
      (async () => {
        try {
          setLoading(true);
          const products = await fetchProducts();
          setItems(products);
        } catch (err) {
          console.error("Ошибка загрузки товаров:", err);
          setError("Не удалось загрузить каталог");
        } finally {
          setLoading(false);
        }
      })();
    }
  }, [isUserLoaded]); // 4. Добавляем зависимость

  const handleBuy = (id) => {
    if (busyId) return;
    setBusyId(id);
    navigate(`/payments/${id}`);
  };

  // 5. Добавляем UI-состояние для проверки сессии
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка сессии…</div>;

  if (loading)
    return <div className={styles.placeholder}>Загрузка каталога…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!items.length)
    return <div className={styles.placeholder}>Товаров пока нет</div>;

  return (
    <div className={styles.grid}>
      {items.map((item) => (
        <article key={item.id} className={styles.card}>
          <div className={styles.pic}>
            <img
              src={item.image_url}
              alt={item.title}
              loading="lazy"
              className={styles.productImage}
            />
          </div>
          <div className={styles.body}>
            <h2 className={styles.title}>{item.title}</h2>
            <p className={styles.desc}>{item.description}</p>
            <div className={styles.priceRow}>
              <span className={styles.price}>{item.price} ₽</span>
            </div>
            <button
              className={styles.buyBtn}
              disabled={busyId === item.id}
              onClick={() => handleBuy(item.id)}
            >
              {busyId === item.id ? "⌛" : "Купить"}
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}
