import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { fetchOrder, payWithRubles } from "../api/orders";
// 👇 Импортируем только нужные функции
import { getStarsInvoice } from "../api/payments";
import { fetchMessages } from "../api/chat";
import { pollOrderStatus } from "../utils/polling";

import styles from "./OrderConfirmation.module.css";

/* приблизительный курс: 1 ⭐ ≈ 2.015 ₽ */
const STAR_RATE = 2.015;

export default function OrderConfirmationPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [order, setOrder] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPay, setShowPay] = useState(false);
  const [processing, setProc] = useState(false);

  /* ─── загрузка заказа + приветственного чата ─── */
  useEffect(() => {
    load();
  }, [orderId]);

  async function load() {
    setLoading(true);
    try {
      const ord = await fetchOrder(orderId);
      const chat = await fetchMessages(orderId);
      setOrder(ord);
      setMessages(chat);
    } catch (err) {
      console.error(err);
      toast.error("Не удалось загрузить заказ или чат");
    } finally {
      setLoading(false);
    }
  }

  /* ─── helper: в чат ─── */
  function goChat(id = orderId) {
    navigate(`/messages/${id}`, { state: { initialMessages: messages } });
  }

  /**
   * ✅ Helper, который ждёт подтверждения оплаты и обновляет страницу.
   */
  const waitForPaymentAndUpdate = async (orderId) => {
    toast.loading("Ожидаем подтверждения оплаты...");
    const isPaid = await pollOrderStatus(orderId);
    toast.dismiss();

    if (isPaid) {
      await load();
    }
    setProc(false);
  };

  /* ─── оплата звёздами ─── */
  async function handleStars() {
    if (!order || processing) return;
    setProc(true);

    try {
      // ✅ УБРАНА ЛИШНЯЯ ЛОГИКА.
      // На этой странице мы всегда работаем с существующим заказом.
      const { order_id, invoice } = await getStarsInvoice(order.id);

      if (!invoice) throw new Error("Сервер не вернул ссылку на счёт");

      (window.Telegram?.WebApp?.openInvoice || window.open)(
        invoice,
        "_blank",
        "noopener,noreferrer",
      );

      await waitForPaymentAndUpdate(order_id);
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Ошибка при оплате звездой");
      setProc(false);
    }
  }

  /* ─── оплата картой (Frikassa) ─── */
  async function handleRubles() {
    if (!order || processing) return;
    setProc(true);

    try {
      const { payment_url } = await payWithRubles(order.id);
      window.open(payment_url, "_blank", "noopener,noreferrer");
      await waitForPaymentAndUpdate(order.id);
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Ошибка оплаты картой");
      setProc(false);
    }
  }

  /* ─── рендер ─── */
  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (!order) return <div className={styles.placeholder}>Заказ не найден</div>;

  const starsPrice = Math.ceil(order.product.price / STAR_RATE);

  return (
    <div className={styles.container}>
      <h1>Ваш заказ #{order.id}</h1>
      <p>
        <strong>Статус:</strong>&nbsp;{order.status}
      </p>

      {order.status === "pending" ? (
        !showPay ? (
          <button className={styles.payButton} onClick={() => setShowPay(true)}>
            Оплатить
          </button>
        ) : (
          <div className={styles.buttons}>
            <button
              className={styles.starsBtn}
              disabled={processing}
              onClick={handleStars}
            >
              ⭐ Оплатить {starsPrice} ⭐
            </button>
            <button
              className={styles.rublesBtn}
              disabled={processing}
              onClick={handleRubles}
            >
              ₽ Оплатить {order.product.price} ₽
            </button>
            <button
              className={styles.cancelBtn}
              onClick={() => setShowPay(false)}
            >
              Отменить
            </button>
          </div>
        )
      ) : (
        <button className={styles.chatBtn} onClick={() => goChat(order.id)}>
          Перейти в чат
        </button>
      )}
    </div>
  );
}
