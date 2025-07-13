import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// 1. Импортируем хук useMe для проверки статуса пользователя
import { useMe } from "../api/auth";
import { fetchUserChats } from "../api/messages";
import styles from "./ChatListPage.module.css";

export default function ChatListPage() {
  /* ──────────── state ──────────── */
  const [chats, setChats] = useState([]);
  const [loading, setLoad] = useState(true);
  const [error, setError] = useState("");

  const nav = useNavigate();

  // 2. Получаем статус загрузки пользователя из React Query
  const { isSuccess: isUserLoaded, isLoading: isUserLoading } = useMe();

  /* ─────────── запрос чатов ─────────── */
  useEffect(() => {
    // 3. Выполняем запрос, ТОЛЬКО если isUserLoaded стал true
    if (isUserLoaded) {
      (async () => {
        try {
          // Устанавливаем loading в true здесь, чтобы показать загрузку чатов
          setLoad(true);
          const list = await fetchUserChats();
          setChats(list);
        } catch (e) {
          console.error("Не удалось загрузить чаты:", e);
          setError(e.message || "Не удалось загрузить чаты");
        } finally {
          setLoad(false);
        }
      })();
    }
  }, [isUserLoaded]); // 4. Добавляем isUserLoaded в зависимости useEffect

  /* ─────────── UI-состояния ─────────── */
  // Пока идёт проверка пользователя, показываем общую загрузку
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка сессии…</div>;

  // Если пользователь проверен, но чаты ещё грузятся
  if (loading) return <div className={styles.placeholder}>Загрузка чатов…</div>;

  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!chats.length)
    return <div className={styles.placeholder}>Чатов пока нет</div>;

  /* ─────────── рендер карточек ─────────── */
  return (
    <div className={styles.container}>
      {chats.map(({ order_id, product_title, content, created_at }) => {
        const go = () => nav(`/messages/${order_id}`);
        const time = created_at ? new Date(created_at).toLocaleString() : "—";
        const snippet = content?.trim()
          ? content.length > 80
            ? content.slice(0, 80) + "…"
            : content
          : "Сообщений пока нет";

        return (
          <div
            key={order_id}
            role="button"
            tabIndex={0}
            className={styles.card}
            onClick={go}
            onKeyDown={(e) => e.key === "Enter" && go()}
          >
            <div className={styles.top}>
              <span className={styles.order}>Заказ&nbsp;#{order_id}</span>
              <span className={styles.time}>{time}</span>
            </div>
            <div className={styles.title}>
              {product_title || "Неизвестный товар"}
            </div>
            <div className={styles.snippet}>{snippet}</div>
          </div>
        );
      })}
    </div>
  );
}
