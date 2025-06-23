// src/pages/admin/AdminChatWindow.jsx
import React, { useState, useRef, useEffect } from "react";
import styles from "./AdminChatWindow.module.css";

export default function AdminChatWindow({ messages, onSend }) {
  const [text, setText] = useState("");
  const bottomRef = useRef();

  // Автопрокрутка вниз
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function submit() {
    if (!text.trim()) return;
    onSend(text.trim());
    setText("");
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.messages}>
        {messages.map((m) => (
          <div
            key={m.id}
            className={
              m.user_id
                ? styles.fromUser // сообщение от юзера
                : styles.fromAdmin // ответ админа
            }
          >
            {m.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <textarea
          className={styles.input}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button className={styles.sendBtn} onClick={submit}>
          Отправить
        </button>
      </div>
    </div>
  );
}
