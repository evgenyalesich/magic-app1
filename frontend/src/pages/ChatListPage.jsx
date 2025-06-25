// src/pages/ChatListPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchUserChats, fetchMessages } from "../api/messages";
import styles from "./ChatListPage.module.css";

export default function ChatListPage() {
  /* ───── state ───── */
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const nav = useNavigate();

  /* ───── первый запрос ───── */
  useEffect(() => {
    (async () => {
      try {
        // 1) получаем список заказов
        const base = await fetchUserChats();

        // 2) если у заказа нет last_message — докачиваем только одно последнее
        const full = await Promise.all(
          base.map(async (c) => {
            if (c.last_message) return c; // всё ок
            const msgs = await fetchMessages(c.order_id);
            return { ...c, last_message: msgs.at(-1) }; // может быть undefined
          }),
        );

        setChats(full);
      } catch (e) {
        setError(e.message || "Не удалось загрузить чаты");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  /* ───── состояния UI ───── */
  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!chats.length)
    return <div className={styles.placeholder}>Чатов пока нет</div>;

  /* ───── основной рендер ───── */
  return (
    <div className={styles.container}>
      {chats.map(({ order_id, product, last_message }) => {
        /* название товара */
        const title = product?.title || "Неизвестный товар";

        /* читаемая дата последнего сообщения */
        const createdAt = last_message?.created_at
          ? new Date(last_message.created_at).toLocaleString()
          : "—";

        /* превью (80 симв.) или fallback */
        const snippet = last_message?.content?.trim()
          ? last_message.content.slice(0, 80) +
            (last_message.content.length > 80 ? "…" : "")
          : "Сообщений пока нет";

        return (
          <div
            key={order_id}
            role="button"
            tabIndex={0}
            className={styles.card}
            onClick={() => nav(`/messages/${order_id}`)}
            onKeyDown={(e) => e.key === "Enter" && nav(`/messages/${order_id}`)}
          >
            <div className={styles.top}>
              <span className={styles.order}>Заказ&nbsp;#{order_id}</span>
              <span className={styles.time}>{createdAt}</span>
            </div>

            <div className={styles.title}>{title}</div>
            <div className={styles.snippet}>{snippet}</div>
          </div>
        );
      })}
    </div>
  );
}
