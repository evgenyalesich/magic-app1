// src/pages/admin/AdminChatWindow.jsx
import React, { useState, useRef, useEffect } from "react";
import styles from "./AdminChatWindow.module.css";

export default function AdminChatWindow({
  messages,
  admin, // объект { telegram_id, … }
  adminId, // fallback
  onSend,
}) {
  const [text, setText] = useState("");
  const bottomRef = useRef(null);

  /* автоскролл вниз */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const submit = () => {
    const trimmed = text.trim();
    if (trimmed) {
      onSend(trimmed);
      setText("");
    }
  };

  /* Ctrl/Cmd+Enter для отправки */
  const handleKey = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      submit();
    }
  };

  const adminTelegramId = admin?.telegram_id ?? adminId;

  return (
    <div className={styles.wrapper}>
      {/* ------- Лента ------- */}
      <div className={styles.messages}>
        {messages.map((m) => {
          if (m.type === "divider") {
            return (
              <div key={m.id} className={styles.divider}>
                {m.label}
              </div>
            );
          }

          const fromAdmin = m.is_admin ?? m.user_id === adminTelegramId;
          const bubbleCls = [
            fromAdmin ? styles.fromAdmin : styles.fromUser,
            m.pending ? styles.pending : "",
          ]
            .filter(Boolean)
            .join(" ");

          return (
            <div key={m.id} className={bubbleCls}>
              {m.content}
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {/* ------- Ввод ------- */}
      <div className={styles.inputRow}>
        <textarea
          className={styles.input}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Введите сообщение…"
        />
        <button className={styles.sendBtn} onClick={submit}>
          Отправить
        </button>
      </div>
    </div>
  );
}
