// src/pages/admin/AdminChatList.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAdminChats } from "../../api/admin"; // GET /api/admin/chats
import styles from "./AdminChatList.module.css";

export default function AdminChatList() {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const nav = useNavigate();

  useEffect(() => {
    fetchAdminChats().then((data) => {
      setChats(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;

  return (
    <div className={styles.container}>
      {chats.map((chat) => (
        <div
          key={chat.order_id}
          className={styles.chatCard}
          onClick={() => nav(`/admin/messages/${chat.order_id}`)}
        >
          <div className={styles.top}>
            <span className={styles.order}>Заказ #{chat.order_id}</span>
            <span className={styles.time}>
              {new Date(chat.last_message.created_at).toLocaleString()}
            </span>
          </div>
          <div className={styles.bottom}>
            <span className={styles.product}>{chat.product.title}</span>
            <span className={styles.snippet}>
              {chat.last_message.content.slice(0, 50)}…
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
