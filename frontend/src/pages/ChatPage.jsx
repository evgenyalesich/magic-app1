// src/pages/ChatPage.jsx
import React, { useState, useEffect, useRef, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import styles from "./ChatPage.module.css";

// 1. Импортируем наш главный хук для авторизации и apiClient
import { useMe } from "../api/auth";
import { apiClient } from "../api/client";
import { sendMessage } from "../api/chat"; // sendMessage всё ещё нужен
import { fetchOrder } from "../api/orders";

export default function ChatPage() {
  const { id: rawId } = useParams();
  const orderId = Number(rawId);
  const navigate = useNavigate();

  // 2. Используем useMe как единый источник данных о пользователе
  const {
    data: user,
    isLoading: isUserLoading,
    isSuccess: isUserReady,
  } = useMe();
  const userId = user?.id; // Берём ID из user, а не из localStorage

  // — общий стейт —
  const [order, setOrder] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [pollError, setPollError] = useState(false);

  const lastSeenRef = useRef("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // 3. Единый useEffect для всей логики загрузки чата
  useEffect(() => {
    // Не запускаем ничего, пока не готовы пользователь и orderId
    if (!isUserReady || Number.isNaN(orderId)) {
      return;
    }

    let isCancelled = false;
    const controller = new AbortController();

    const loadAndPoll = async () => {
      // --- Начальная загрузка ---
      try {
        if (isCancelled) return;
        setLoading(true);
        const initialMsgs = (
          await apiClient.get(`/messages/${orderId}`, {
            signal: controller.signal,
          })
        ).data;
        if (isCancelled) return;

        setMessages(initialMsgs);
        lastSeenRef.current = initialMsgs.at(-1)?.created_at || "";

        if (!initialMsgs.length || !initialMsgs[0]?.product_title) {
          const ord = await fetchOrder(orderId);
          if (!isCancelled) setOrder(ord);
        }
      } catch (err) {
        if (isCancelled) return;
        if (err.response?.status === 403)
          setLoadError("У вас нет доступа к этому чату");
        else setLoadError("Не удалось загрузить чат");
      } finally {
        if (!isCancelled) setLoading(false);
      }

      // --- Long-polling ---
      while (!isCancelled) {
        try {
          const pollUrl = `/messages/${orderId}/poll?after=${encodeURIComponent(
            lastSeenRef.current,
          )}`;
          const news = (
            await apiClient.get(pollUrl, { signal: controller.signal })
          ).data;

          if (news.length && !isCancelled) {
            setMessages((prev) => {
              const known = new Set(prev.map((m) => m.id));
              const uniq = news.filter((n) => !known.has(n.id));
              return [...prev, ...uniq];
            });
            lastSeenRef.current = news.at(-1).created_at;
          }
          if (!isCancelled) setPollError(false);
        } catch (err) {
          if (!isCancelled && err.name !== "AbortError") {
            setPollError(true);
          }
        }
        await new Promise((r) => setTimeout(r, 2000)); // Задержка между запросами
      }
    };

    loadAndPoll();

    return () => {
      isCancelled = true;
      controller.abort();
    };
  }, [isUserReady, orderId, navigate]); // 4. Правильные зависимости

  // ─── Автоскролл вниз ───────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ─── Отправка нового сообщения ────────────────────────────
  const handleSend = async () => {
    const content = inputRef.current?.value.trim();
    if (!content) return;

    const tmpId = `tmp-${Date.now()}`;
    const tmpMsg = {
      id: tmpId,
      content,
      user_id: userId,
      is_admin: false,
      created_at: new Date().toISOString(),
      pending: true,
    };
    setMessages((prev) => [...prev, tmpMsg]);
    inputRef.current.value = "";

    try {
      const real = await sendMessage(orderId, content, tmpId);
      setMessages((prev) => prev.map((m) => (m.id === tmpId ? real : m)));
      lastSeenRef.current = real.created_at;
    } catch {
      setLoadError("Не удалось отправить сообщение");
      setMessages((prev) => prev.filter((m) => m.id !== tmpId));
    }
  };

  // ─── Разделители по автору ─────────────────────────────────
  const display = useMemo(() => {
    if (!messages.length) return [];
    const out = [];
    let lastAuthor = null;
    messages.forEach((m, i) => {
      const author =
        m.user_id === userId ? "me" : m.is_admin ? "admin" : "user";
      if (author !== lastAuthor) {
        out.push({
          id: `div-${i}`,
          type: "divider",
          label:
            author === "me"
              ? "Вы"
              : author === "admin"
                ? "Администратор"
                : "Пользователь",
        });
        lastAuthor = author;
      }
      out.push(m);
    });
    return out;
  }, [messages, userId]);

  // --- 5. Обновлённые UI-состояния ---
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка сессии…</div>;
  if (loading) return <div className={styles.placeholder}>Загрузка чата…</div>;
  if (loadError) return <div className={styles.placeholder}>{loadError}</div>;

  const productTitle =
    messages[0]?.product_title || order?.product?.title || "Неизвестный товар";

  return (
    <div className={styles.page}>
      <h1 className={styles.header}>
        Заказ #{orderId} — «{productTitle}»
        {pollError && <span className={styles.pollError}> • нет связи</span>}
      </h1>

      <div className={styles.messageList}>
        {display.map((m) =>
          m.type === "divider" ? (
            <div key={m.id} className={styles.divider}>
              {m.label}
            </div>
          ) : (
            <div
              key={m.id}
              className={[
                styles.message,
                m.user_id === userId
                  ? styles.own
                  : m.is_admin
                    ? styles.admin
                    : styles.user,
                m.pending ? styles.pending : "",
              ].join(" ")}
            >
              <div className={styles.messageText}>{m.content}</div>
              <div className={styles.messageTime}>
                {new Date(m.created_at).toLocaleTimeString()}
                {m.is_admin && <span className={styles.adminBadge}>Админ</span>}
              </div>
            </div>
          ),
        )}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputArea}>
        <input
          ref={inputRef}
          className={styles.input}
          placeholder="Ваше сообщение…"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button onClick={handleSend} className={styles.sendButton}>
          Отправить
        </button>
      </div>
    </div>
  );
}
