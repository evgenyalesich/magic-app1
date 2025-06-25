// src/pages/OrderConfirmationPage.jsx
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchOrder } from "../api/orders"; // только чтение заказа
import { initPayment } from "../api/payments"; // invoice для ⭐
import { payWithRubles } from "../api/orders"; // оплата ₽
import styles from "./OrderConfirmationPage.module.css";

export default function OrderConfirmationPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOptions, setShowOptions] = useState(false);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadOrder();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId]);

  async function loadOrder() {
    setLoading(true);
    try {
      const data = await fetchOrder(orderId);
      setOrder(data);
    } catch (err) {
      console.error(err);
      alert("Не удалось загрузить заказ");
    } finally {
      setLoading(false);
      setShowOptions(false);
      setProcessing(false);
    }
  }

  // примерный курс 1 ⭐ ≈ 2.015 ₽
  const starsCost = order ? Math.ceil(order.product.price / 2.015) : 0;

  /** Оплатить звёздами – запрашиваем invoice и открываем его через WebApp API */
  async function handlePayStars() {
    setProcessing(true);
    try {
      const { invoice } = await initPayment(order.product.id);
      if (window?.Telegram?.WebApp?.openInvoice) {
        window.Telegram.WebApp.openInvoice(invoice);
      } else {
        alert("Telegram WebApp API недоступен – откройте страницу из бота");
      }
    } catch (err) {
      console.error(err);
      alert("Не удалось инициировать оплату звёздами: " + err.message);
    } finally {
      // через webhook статус станет paid – попробуем перезагрузить
      setTimeout(loadOrder, 2000);
    }
  }

  /** Оплатить рублями через внешний шлюз */
  async function handlePayRubles() {
    setProcessing(true);
    try {
      const { payment_url } = await payWithRubles(orderId);
      window.location.href = payment_url;
    } catch (err) {
      console.error(err);
      alert("Не удалось оплатить рублями: " + err.message);
      setProcessing(false);
    }
  }

  function handleOpenChat() {
    navigate(`/messages/${orderId}`);
  }

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (!order) return <div className={styles.placeholder}>Заказ не найден</div>;

  return (
    <div className={styles.container}>
      <h1>Ваш заказ #{order.id}</h1>

      <div className={styles.product}>
        <img
          src={order.product.image_url}
          alt={order.product.title}
          className={styles.image}
        />
        <div className={styles.details}>
          <h2>{order.product.title}</h2>
          <p>{order.product.description}</p>
          <p>
            <strong>Цена:</strong> {order.product.price} ₽ ({starsCost} ⭐)
          </p>
        </div>
      </div>

      <p>
        <strong>Статус заказа:</strong> {order.status}
      </p>

      {order.status === "pending" ? (
        !showOptions ? (
          <button
            className={styles.payButton}
            onClick={() => setShowOptions(true)}
          >
            Оплатить
          </button>
        ) : (
          <div className={styles.options}>
            <button
              onClick={handlePayStars}
              disabled={processing}
              className={styles.starsButton}
            >
              ⭐ Оплатить {starsCost} ⭐
            </button>
            <button
              onClick={handlePayRubles}
              disabled={processing}
              className={styles.rublesButton}
            >
              ₽ Оплатить {order.product.price} ₽
            </button>
            <button
              onClick={() => setShowOptions(false)}
              className={styles.cancelButton}
            >
              Отмена
            </button>
          </div>
        )
      ) : (
        <button onClick={handleOpenChat} className={styles.chatButton}>
          Перейти в чат
        </button>
      )}
    </div>
  );
}
