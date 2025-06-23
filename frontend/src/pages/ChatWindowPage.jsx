import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { fetchMessages, sendMessage } from "../api/messages";
import { useCurrentUser } from "../hooks/useCurrentUser";
import styles from "./ChatWindowPage.module.css";

export default function ChatWindowPage() {
  const { orderId } = useParams();
  const me = useCurrentUser();
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState("");
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef();

  // загрузка истории
  useEffect(() => {
    (async () => {
      try {
        const msgs = await fetchMessages(orderId);
        setMessages(msgs);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    })();
  }, [orderId]);

  // автo-прокрутка вниз при новых сообщениях
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const text = newMsg.trim();
    if (!text) return;
    try {
      const msg = await sendMessage(orderId, text);
      setMessages((prev) => [...prev, msg]);
      setNewMsg("");
    } catch (err) {
      console.error(err);
      alert("Не удалось отправить сообщение");
    }
  };

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;

  return (
    <div className={styles.page}>
      <div className={styles.header}>Чат по заказу #{orderId}</div>
      <div className={styles.messages}>
        {messages.map((m) => {
          const isMe = me && m.user_id === me.id;
          return (
            <div
              key={m.id}
              className={isMe ? styles.messageRight : styles.messageLeft}
            >
              <div className={styles.bubble}>{m.content}</div>
              <div className={styles.time}>
                {new Date(m.created_at).toLocaleTimeString()}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
      <div className={styles.inputRow}>
        <input
          value={newMsg}
          onChange={(e) => setNewMsg(e.target.value)}
          placeholder="Ваше сообщение…"
          className={styles.input}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend} className={styles.sendBtn}>
          Отправить
        </button>
      </div>
    </div>
  );
}
