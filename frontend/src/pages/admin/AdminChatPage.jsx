import React, { useState, useEffect, useMemo, useRef } from "react";
import { useParams, Link } from "react-router-dom";

// 1. Импортируем хук useMe, а fetchMe нам больше не нужен
import { useMe } from "../../api/auth";
import AdminChatWindow from "./AdminChatWindow";
import { fetchAdminMessages, sendAdminMessage } from "../../api/admin";

const WELCOME =
  "Добрый день! Чтобы получить ваш расклад, " +
  "пожалуйста, пришлите ваше имя, дату рождения и ваш вопрос.";
const POLL_DELAY = 2000; // Увеличим задержку для стабильности

export default function AdminChatPage() {
  const { orderId } = useParams();

  // --- 2. Получаем админа через хук, а не через useEffect ---
  const { data: admin, isLoading: isAdminLoading, isError } = useMe();

  const [messages, setMsgs] = useState([]);
  const [loading, setLoading] = useState(true); // Для первоначальной загрузки чата
  const [error, setError] = useState("");
  const [pollError, setPollError] = useState(false);

  const lastSeenRef = useRef("");

  // --- 3. Единый useEffect для всей логики загрузки чата ---
  useEffect(() => {
    // Не делаем ничего, пока не загружен админ или нет ID заказа
    if (!admin || !orderId) {
      return;
    }

    const controller = new AbortController();
    let isCancelled = false;

    // --- Загрузка стартовой истории сообщений ---
    const loadInitialMessages = async () => {
      try {
        if (isCancelled) return;
        setLoading(true);

        let msgs = await fetchAdminMessages(
          orderId,
          "",
          false,
          controller.signal,
        );

        // Отправляем приветственное сообщение, если чат пуст
        if (!msgs.length) {
          const welcome = await sendAdminMessage(orderId, WELCOME);
          msgs = [welcome];
        }

        if (!isCancelled) {
          setMsgs(msgs);
          // Устанавливаем метку последнего сообщения для long-polling
          lastSeenRef.current = msgs.at(-1)?.created_at || "";
        }
      } catch (err) {
        if (!isCancelled) {
          const status = err.response?.status;
          setError(
            status === 404 ? "Чат не найден" : "Не удалось загрузить чат",
          );
        }
      } finally {
        if (!isCancelled) setLoading(false);
      }
    };

    // --- Long-polling для получения новых сообщений ---
    const pollNewMessages = async () => {
      while (!isCancelled) {
        try {
          const news = await fetchAdminMessages(
            orderId,
            lastSeenRef.current,
            true, // usePoll = true
            controller.signal,
          );

          if (news.length && !isCancelled) {
            setMsgs((prev) => {
              const known = new Set(prev.map((m) => m.id));
              const uniqueNews = news.filter((n) => !known.has(n.id));
              if (uniqueNews.length === 0) return prev;
              return [...prev, ...uniqueNews];
            });
            lastSeenRef.current = news.at(-1).created_at;
          }
          if (!isCancelled) setPollError(false);
        } catch (err) {
          if (!isCancelled && err.name !== "AbortError") {
            setPollError(true);
          }
        }
        await new Promise((r) => setTimeout(r, POLL_DELAY));
      }
    };

    // Запускаем цепочку: сначала грузим историю, потом начинаем опрос
    loadInitialMessages().then(() => {
      if (!isCancelled) {
        pollNewMessages();
      }
    });

    // Очистка при размонтировании
    return () => {
      isCancelled = true;
      controller.abort();
    };
  }, [orderId, admin]); // Зависимость от admin и orderId

  // ─── Отправка нового сообщения ──────────────────────────────
  const handleSend = async (text) => {
    if (!admin) return;

    const tmpId = `tmp-${Date.now()}`;
    const tmpMsg = {
      id: tmpId,
      content: text,
      user_id: admin.id,
      is_admin: true,
      created_at: new Date().toISOString(),
      pending: true,
    };
    setMsgs((prev) => [...prev, tmpMsg]);

    try {
      const real = await sendAdminMessage(orderId, text, tmpId);
      setMsgs((prev) => prev.map((m) => (m.id === tmpId ? real : m)));
      lastSeenRef.current = real.created_at;
    } catch {
      setError("Не удалось отправить сообщение");
      setMsgs((prev) => prev.filter((m) => m.id !== tmpId));
    }
  };

  // ─── Разделители «Администратор / Пользователь» ────────────
  const display = useMemo(() => {
    const out = [];
    let lastIsAdmin = null;
    messages.forEach((m, i) => {
      const isAdm = m.is_admin ?? m.user_id === admin?.id;
      if (lastIsAdmin === null || isAdm !== lastIsAdmin) {
        out.push({
          id: `div-${i}`,
          type: "divider",
          label: isAdm ? "Администратор" : "Пользователь",
        });
        lastIsAdmin = isAdm;
      }
      out.push(m);
    });
    return out;
  }, [messages, admin]);

  // --- 4. Обновлённые UI-состояния ---
  if (isAdminLoading)
    return <div style={{ padding: 20 }}>Проверка доступа…</div>;
  if (isError)
    return (
      <div style={{ padding: 20 }}>
        Не удалось проверить права администратора
      </div>
    );

  if (loading) return <div style={{ padding: 20 }}>Загрузка чата…</div>;
  if (error) {
    return (
      <div style={{ padding: 20 }}>
        <Link to="/admin/messages">← ко всем чатам</Link>
        <div style={{ color: "red", marginTop: 10 }}>{error}</div>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: 20,
        display: "flex",
        flexDirection: "column",
        height: "calc(100vh - 40px)",
      }}
    >
      <Link to="/admin/messages">← ко всем чатам</Link>
      <h2 style={{ display: "flex", alignItems: "center", gap: 8 }}>
        Чат заказа #{orderId}
        {pollError && (
          <span style={{ color: "#d94747", fontSize: 14 }}>• нет связи</span>
        )}
      </h2>

      {admin ? (
        <AdminChatWindow messages={display} admin={admin} onSend={handleSend} />
      ) : (
        <div>Загрузка профиля…</div>
      )}
    </div>
  );
}
