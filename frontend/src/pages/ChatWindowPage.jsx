import React, { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchMessages, sendMessage } from "../api/chat";
import { fetchOrder } from "../api/orders";
import { useCurrentUser } from "../hooks/useCurrentUser";
import styles from "./ChatWindowPage.module.css";

export default function ChatWindowPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const me = useCurrentUser();

  const [order, setOrder] = useState(null);
  const [messages, setMsgs] = useState([]);
  const [loading, setLoad] = useState(true);
  const [error, setErr] = useState("");

  const lastSeenRef = useRef("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  /* ---------- 1. стартовая история ---------- */
  useEffect(() => {
    if (!orderId) return;
    (async () => {
      try {
        const msgs = await fetchMessages(orderId);
        setMsgs(msgs);
        if (msgs.length) lastSeenRef.current = msgs.at(-1).created_at;

        if (!msgs.length || !msgs[0]?.product_title) {
          const ord = await fetchOrder(orderId);
          setOrder(ord);
        }
      } catch {
        setErr("Не удалось загрузить чат");
      } finally {
        setLoad(false);
      }
    })();
  }, [orderId]);

  /* ---------- 2. long-poll ---------- */
  useEffect(() => {
    if (!orderId || !me) return; // Не запускаем опрос, пока не загружен пользователь
    let aborted = false;
    let controller = new AbortController();

    const poll = async () => {
      if (aborted) return;
      try {
        const news = await fetchMessages(
          orderId,
          lastSeenRef.current,
          true, // use /poll
          controller.signal,
        );

        // ✅ ИСПРАВЛЕНИЕ: Добавляем умную фильтрацию, чтобы избежать дублирования
        if (news.length) {
          setMsgs((prev) => {
            const knownIds = new Set(prev.map((m) => m.id));
            // Фильтруем сообщения:
            // 1. Убираем дубликаты (если сообщение с таким ID уже есть).
            // 2. Убираем свои же сообщения (их добавляет функция отправки).
            const uniqueNewsFromOthers = news.filter(
              (n) => !knownIds.has(n.id) && n.user_id !== me.id,
            );

            // Если нет новых сообщений от других, состояние не меняем.
            if (uniqueNewsFromOthers.length === 0) {
              return prev;
            }
            return [...prev, ...uniqueNewsFromOthers];
          });
          lastSeenRef.current = news.at(-1).created_at;
        }
      } catch (e) {
        if (e.name !== "AbortError") console.warn("poll error", e);
      }
      if (!aborted) {
        controller = new AbortController();
        poll();
      }
    };
    poll();

    return () => {
      aborted = true;
      controller.abort();
    };
  }, [orderId, me]); // Добавляем 'me' в зависимости

  /* ---------- 3. автоскролл ---------- */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* ---------- 4. отправка ---------- */
  const handleSend = async () => {
    const text = inputRef.current?.value.trim();
    if (!text || !me) return; // Не отправляем, если нет текста или пользователя

    const tmpId = `tmp-${Date.now()}`;
    const tmpMsg = {
      id: tmpId,
      content: text,
      user_id: me.id, // Используем ID из 'me'
      is_admin: me.is_admin,
      created_at: new Date().toISOString(),
      pending: true,
    };
    setMsgs((p) => [...p, tmpMsg]);
    inputRef.current.value = "";

    try {
      const real = await sendMessage(orderId, text, tmpId);
      setMsgs((p) => p.map((m) => (m.id === tmpId ? real : m)));
      lastSeenRef.current = real.created_at;
    } catch {
      setErr("Не удалось отправить сообщение");
      setMsgs((p) => p.filter((m) => m.id !== tmpId));
    }
  };

  /* ---------- UI ---------- */
  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        Чат по заказу #{orderId} — «{order?.product?.title ?? "..."}»
      </div>

      <div className={styles.messages}>
        {messages.map((m) => {
          const isMe = me && m.user_id === me.id;
          return (
            <div
              key={m.id}
              className={isMe ? styles.messageRight : styles.messageLeft}
            >
              <div
                className={[
                  styles.bubble,
                  m.pending ? styles.pending : "",
                ].join(" ")}
              >
                {m.content}
              </div>
              <div className={styles.time}>
                {new Date(m.created_at).toLocaleTimeString()}
                {m.is_admin && <span className={styles.adminBadge}>Админ</span>}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <input
          ref={inputRef}
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
