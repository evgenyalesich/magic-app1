// frontend/src/pages/ChatPage.jsx
import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { fetchMessages, sendMessage } from "../api/chat";
import styles from "./ChatPage.module.css";

export default function ChatPage() {
  const { orderId } = useParams();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    fetchMessages(orderId).then(setMessages);
  }, [orderId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!text.trim()) return;
    const msg = await sendMessage(orderId, text);
    setMessages((prev) => [...prev, msg]);
    setText("");
  };

  return (
    <div className={styles.page}>
      <h1 className={styles.header}>Чат по заказу №{orderId}</h1>

      <div className={styles.messageList}>
        {messages.map((m) => (
          <div
            key={m.id}
            className={`${styles.message} ${
              m.is_admin ? styles.admin : styles.user
            }`}
          >
            <div className={styles.messageText}>{m.content}</div>
            <div className={styles.messageTime}>
              {new Date(m.created_at).toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputArea}>
        <input
          type="text"
          placeholder="Ваше сообщение..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className={styles.input}
        />
        <button onClick={handleSend} className={styles.sendButton}>
          Отправить
        </button>
      </div>
    </div>
  );
}
