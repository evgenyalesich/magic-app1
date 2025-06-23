import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchUserChats } from "../api/orders";

import styles from "./ChatListPage.module.css";

export default function ChatListPage() {
  const [chats, setChats] = useState([]); // будет массив объектов вида MessageSchema
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const msgs = await fetchUserChats();

        // сгруппируем по order_id, выберем для каждого чата самое свежее сообщение
        const lastByOrder = msgs.reduce((acc, msg) => {
          const key = msg.order_id;
          if (
            !acc[key] ||
            new Date(msg.created_at) > new Date(acc[key].created_at)
          ) {
            acc[key] = msg;
          }
          return acc;
        }, {});

        // приведём к списку чатов
        const list = Object.values(lastByOrder).map((msg) => ({
          orderId: msg.order_id,
          lastMessage: msg.content,
          status: msg.status, // если back отдаёт status заказа вместе с message
          updatedAt: msg.created_at,
        }));

        setChats(list);
      } catch {
        setError("Не удалось загрузить чаты");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!chats.length)
    return <div className={styles.placeholder}>Чатов пока нет</div>;

  return (
    <div className={styles.container}>
      {chats.map((chat) => (
        <Link
          key={chat.orderId}
          to={`/messages/${chat.orderId}`}
          className={styles.chatItem}
        >
          <div className={styles.chatInfo}>
            <div className={styles.title}>Заказ #{chat.orderId}</div>
            <div className={styles.subtitle}>
              {chat.status === "pending" ? "Ожидает оплаты" : "Переписка"}
            </div>
            <div className={styles.preview}>{chat.lastMessage}</div>
          </div>
        </Link>
      ))}
    </div>
  );
}
