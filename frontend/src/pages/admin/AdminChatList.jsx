// frontend/src/pages/admin/AdminChatList.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// 1. Импортируем хук useMe для проверки авторизации
import { useMe } from "../../api/auth";
import { fetchAdminChats, deleteAdminChat } from "../../api/admin";
import styles from "./AdminChatList.module.css";

export default function AdminChatList() {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const nav = useNavigate();

  // 2. Получаем статус пользователя. AdminLayout уже проверил, что он админ,
  //    но нам нужен этот хук как сигнал, что проверка завершена.
  const { isSuccess: isUserReady, isLoading: isUserLoading } = useMe();

  // 3. Объединяем логику загрузки и обновления в одном useEffect
  useEffect(() => {
    // 4. Запускаем загрузку и интервал только после подтверждения авторизации
    if (isUserReady) {
      let isCancelled = false;

      const load = async () => {
        try {
          // Показываем индикатор загрузки только при первом вызове,
          // чтобы фоновые обновления были незаметными.
          if (!isCancelled && !chats.length) setLoading(true);
          const data = await fetchAdminChats();
          if (!isCancelled) setChats(data);
        } catch (e) {
          if (!isCancelled) {
            console.error("Не удалось загрузить чаты:", e);
            setError("Не удалось загрузить чаты");
          }
        } finally {
          if (!isCancelled) setLoading(false);
        }
      };

      load(); // Загружаем чаты сразу
      const tid = setInterval(load, 60_000); // И ставим на периодическое обновление

      // Очистка при размонтировании компонента
      return () => {
        isCancelled = true;
        clearInterval(tid);
      };
    }
  }, [isUserReady]); // 5. Добавляем зависимость от статуса пользователя

  // удаление целого диалога
  const handleDeleteChat = async (orderId) => {
    if (
      !window.confirm(
        `Удалить весь диалог заказа #${orderId}? Это действие необратимо.`,
      )
    ) {
      return;
    }
    try {
      await deleteAdminChat(orderId);
      setChats((prev) => prev.filter((c) => c.order_id !== orderId));
    } catch (e) {
      console.error("Не удалось удалить диалог:", e);
      alert("Ошибка при удалении диалога");
    }
  };

  // 6. Добавляем UI-состояние для проверки доступа
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка доступа…</div>;
  if (loading) return <div className={styles.placeholder}>Загрузка чатов…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!chats.length)
    return <div className={styles.placeholder}>Активных чатов нет</div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Сообщения покупателей</h2>
        <span className={styles.count}>{chats.length} чат(ов)</span>
      </div>

      <div className={styles.chatList}>
        {chats.map((chat) => {
          const {
            order_id,
            product_title,
            content,
            created_at,
            unread_count,
            user_name,
          } = chat;
          const time = formatTime(created_at);
          const snippet = content?.trim() || "Нет сообщений";
          const isUnread = Number(unread_count) > 0;

          return (
            <div
              key={order_id}
              className={`${styles.chatCard} ${isUnread ? styles.unread : ""}`}
              onClick={() => nav(`/admin/messages/${order_id}`)}
            >
              <div className={styles.cardHeader}>
                <div className={styles.orderInfo}>
                  <span className={styles.orderNumber}>#{order_id}</span>
                  {isUnread && (
                    <span className={styles.unreadBadge}>{unread_count}</span>
                  )}
                </div>
                <span className={styles.timestamp}>{time}</span>
              </div>

              <div className={styles.cardContent}>
                <div className={styles.productTitle}>{product_title}</div>
                <div className={styles.messageSnippet}>
                  {snippet.length <= 60 ? snippet : `${snippet.slice(0, 60)}…`}
                </div>
              </div>

              <div className={styles.cardFooter}>
                <span className={styles.customerLabel}>
                  Покупатель • {user_name || "Неизвестный"}
                </span>
                <span className={styles.arrow}>→</span>
              </div>

              <button
                className={styles.deleteChatBtn}
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteChat(order_id);
                }}
              >
                Удалить диалог
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// helper для форматирования
function formatTime(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  const diff = (Date.now() - d.getTime()) / 1000;
  const m = Math.floor(diff / 60);
  const h = Math.floor(m / 60);
  const dd = Math.floor(h / 24);
  if (m < 1) return "Только что";
  if (m < 60) return `${m} мин назад`;
  if (h < 24) return `${h} ч назад`;
  if (dd < 7) return `${dd} дн назад`;
  return d.toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
  });
}
