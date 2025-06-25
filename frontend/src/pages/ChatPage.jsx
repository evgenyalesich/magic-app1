// src/pages/ChatPage.jsx
import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";

import { fetchMessages, sendMessage } from "../api/messages";
import { fetchOrder } from "../api/orders";

import styles from "./ChatPage.module.css";

export default function ChatPage() {
  /* ───── params ───── */
  const { id: rawId } = useParams(); // <Route path="/messages/:id" …>
  const orderId = Number(rawId);
  const nav = useNavigate();

  /* ───── state ───── */
  const [order, setOrder] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  /* ───── helpers ───── */
  const scrollDown = () =>
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });

  const loadData = useCallback(async () => {
    try {
      const [ord, msgs] = await Promise.all([
        fetchOrder(orderId),
        fetchMessages(orderId),
      ]);
      setOrder(ord);
      setMessages(msgs);
      setError("");
    } catch (e) {
      console.error(e);
      setError("Не удалось загрузить чат");
    } finally {
      setLoading(false);
    }
  }, [orderId]);

  /* ───── guards ───── */
  useEffect(() => {
    if (Number.isNaN(orderId)) nav("/messages"); // неверный id → назад к списку
  }, [orderId, nav]);

  /* ───── first load & polling ───── */
  useEffect(() => {
    if (Number.isNaN(orderId)) return;
    loadData(); // первый вызов
    const t = setInterval(loadData, 10_000); // опциональный авто-пулл
    return () => clearInterval(t);
  }, [orderId, loadData]);

  /* ───── auto-scroll on new messages ───── */
  useEffect(scrollDown, [messages]);

  /* ───── send message ───── */
  const handleSend = async () => {
    const content = text.trim();
    if (!content) return;
    try {
      const msg = await sendMessage(orderId, content);
      setMessages((prev) => [...prev, msg]);
      setText("");
      inputRef.current?.focus();
    } catch (e) {
      console.error(e);
      setError("Сообщение не отправлено");
    }
  };

  /* ───── UI states ───── */
  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;

  const productTitle = order?.product?.title ?? "Неизвестный товар";

  /* ───── render ───── */
  return (
    <div className={styles.page}>
      <h1 className={styles.header}>
        Заказ #{orderId} — «{productTitle}»
      </h1>

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
          ref={inputRef}
          type="text"
          placeholder="Ваше сообщение…"
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
