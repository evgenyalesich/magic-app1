// src/pages/admin/AdminMessagesPage.jsx
import React, { useEffect, useState } from "react";
import styles from "./AdminMessagesPage.module.css";
import { fetchAdminMessages, deleteAdminMessage } from "../../api/admin";

export default function AdminMessagesPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadMessages();
  }, []);

  async function loadMessages() {
    setLoading(true);
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

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;

  return (
    <div className={styles.container}>
      {messages.length > 0 ? (
        messages.map((m) => (
          <div key={m.id} className={styles.card}>
            <div className={styles.header}>
              <span className={styles.from}>{m.from_name}</span>
              <span className={styles.date}>
                {new Date(m.created_at).toLocaleString()}
              </span>
            </div>
            <div className={styles.body}>{m.text}</div>
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
