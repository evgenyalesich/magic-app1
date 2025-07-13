// src/pages/admin/AdminMessagesPage.jsx
import React, { useEffect, useState } from "react";
import styles from "./AdminMessagesPage.module.css";
// 1. Импортируем хук useMe
import { useMe } from "../../api/auth";
import { fetchAdminMessages, deleteAdminMessage } from "../../api/admin";

export default function AdminMessagesPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 2. Получаем статус авторизации
  const { isSuccess: isUserReady, isLoading: isUserLoading } = useMe();

  async function loadMessages() {
    // setLoading(true) перенесено в useEffect, чтобы не было лишних состояний
    setError("");
    try {
      const data = await fetchAdminMessages();
      setMessages(data);
    } catch (err) {
      console.error(err);
      setError("Не удалось загрузить сообщения");
    } finally {
      setLoading(false);
    }
  }

  // 3. Запускаем загрузку только после проверки пользователя
  useEffect(() => {
    if (isUserReady) {
      loadMessages();
    }
  }, [isUserReady]); // 4. Добавляем зависимость

  async function handleDelete(id) {
    if (!window.confirm("Точно удалить сообщение?")) return;
    try {
      await deleteAdminMessage(id);
      setMessages((msgs) => msgs.filter((m) => m.id !== id));
    } catch (err) {
      console.error(err);
      alert("Не удалось удалить сообщение: " + err.message);
    }
  }

  // 5. Добавляем UI-состояния для проверки и загрузки
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка доступа…</div>;
  if (loading)
    return <div className={styles.placeholder}>Загрузка сообщений…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;

  return (
    <div className={styles.container}>
      {messages.length > 0 ? (
        messages.map((m) => (
          <div key={m.id} className={styles.card}>
            <div className={styles.header}>
              <span className={styles.from}>
                Заказ #{m.order_id} — {m.product_title} — {m.user_name}
              </span>
              <span className={styles.date}>
                {new Date(m.created_at).toLocaleString()}
              </span>
            </div>
            <div className={styles.body}>{m.content}</div>
            <button
              className={styles.deleteButton}
              onClick={() => handleDelete(m.id)}
            >
              Удалить
            </button>
          </div>
        ))
      ) : (
        <div className={styles.placeholder}>Нет новых сообщений</div>
      )}
    </div>
  );
}
