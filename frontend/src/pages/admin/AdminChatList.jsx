// frontend/src/pages/admin/AdminChatList.jsx
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAdminChats } from "../../api/admin";
import styles from "./AdminChatList.module.css";

export default function AdminChatList() {
  /* ─────────── state ─────────── */
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const nav = useNavigate();

  /* ─────── загрузка + авто-polling ─────── */
  const loadChats = useCallback(async () => {
    try {
      const data = await fetchAdminChats(); // GET /api/admin/chats
      setChats(data);
      setError("");
    } catch (e) {
      console.error(e);
      setError(e.message || "Не удалось загрузить чаты");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadChats(); // первый запрос
    const id = setInterval(loadChats, 10_000);
    return () => clearInterval(id); // очистка таймера
  }, [loadChats]);

  /* ─────── UI состояния ─────── */
  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!chats.length)
    return <div className={styles.placeholder}>Чатов пока нет</div>;

  /* ─────── основной рендер ─────── */
  return (
    <div className={styles.container}>
      {chats.map(({ order_id, product, last_message }) => {
        const title = product?.title ?? "Неизвестный товар";
        const when = last_message?.created_at
          ? new Date(last_message.created_at).toLocaleString()
          : "—";
        const snippet = last_message?.content?.trim()
          ? last_message.content.slice(0, 50) +
            (last_message.content.length > 50 ? "…" : "")
          : "Нет сообщений";

        return (
          <button
            key={order_id}
            type="button"
            className={styles.chatCard}
            onClick={() => nav(`/admin/messages/${order_id}`)}
          >
            <div className={styles.top}>
              <span className={styles.order}>Заказ&nbsp;#{order_id}</span>
              <span className={styles.time}>{when}</span>
            </div>

            <div className={styles.bottom}>
              <span className={styles.product}>{title}</span>
              <span className={styles.snippet}>{snippet}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
