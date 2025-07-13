// frontend/src/pages/PurchaseHistoryPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// 1. Импортируем хук useMe для проверки статуса авторизации
import { useMe } from "../api/auth";
import { fetchPurchaseHistory } from "../api/orders";
import styles from "./PurchaseHistoryPage.module.css";

export default function PurchaseHistoryPage() {
  /* ───── state ───── */
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const nav = useNavigate();

  // 2. Получаем статус загрузки пользователя
  const { isSuccess: isUserLoaded, isLoading: isUserLoading } = useMe();

  /* ───── fetch once ───── */
  useEffect(() => {
    // 3. Выполняем запрос, только если пользователь успешно загружен
    if (isUserLoaded) {
      (async () => {
        try {
          setLoading(true); // Начинаем загрузку истории
          const data = await fetchPurchaseHistory(); // GET /api/orders/my
          setOrders(data);
        } catch (e) {
          console.error(e);
          setError(e.message || "Не удалось загрузить историю");
        } finally {
          setLoading(false); // Завершаем загрузку истории
        }
      })();
    }
  }, [isUserLoaded]); // 4. Добавляем isUserLoaded в массив зависимостей

  /* ───── UI-состояния ───── */
  // Пока идёт проверка пользователя, показываем статус
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка сессии…</div>;

  // Если пользователь проверен, но история ещё грузится
  if (loading)
    return <div className={styles.placeholder}>Загрузка истории…</div>;

  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!orders.length)
    return (
      <div className={styles.placeholder}>Пока ничего не куплено&nbsp;🙂</div>
    );

  /* ───── helpers ───── */
  const openChat = (id) => nav(`/messages/${id}`);

  /* ───── render ───── */
  return (
    <div className={styles.container}>
      {orders.map((o) => {
        const {
          id,
          total,
          created_at,
          product: { title, image_url = "" } = {},
        } = o;

        const dateFmt = new Date(created_at).toLocaleString();

        return (
          <article key={id} className={styles.card}>
            <img
              src={image_url || "/img/placeholder.webp"}
              alt={title}
              className={styles.image}
              loading="lazy"
            />
            <div className={styles.content}>
              <h2 className={styles.title}>{title}</h2>
              <div className={styles.meta}>
                <span className={styles.date}>{dateFmt}</span>
                <span className={styles.sum}>{Number(total).toFixed(2)} ₽</span>
              </div>
              <button className={styles.chatBtn} onClick={() => openChat(id)}>
                Открыть чат
              </button>
            </div>
          </article>
        );
      })}
    </div>
  );
}
