// frontend/src/pages/OrderConfirmation.jsx
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchOrder } from "../api/orders";
import styles from "./OrderConfirmation.module.css";

export default function OrderConfirmation() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchOrder(orderId)
      .then(setOrder)
      .catch((err) => setError(err.message));
  }, [orderId]);

  if (error) {
    return <p className={styles.error}>Ошибка: {error}</p>;
  }

  if (!order) {
    return <p className={styles.loading}>Загрузка...</p>;
  }

  const { product, status, created_at, id } = order;

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Заказ №{id}</h1>

      <div className={styles.detailRow}>
        <span className={styles.label}>Услуга: </span>
        <span className={styles.value}>{product.name}</span>
      </div>

      <div className={styles.detailRow}>
        <span className={styles.label}>Описание: </span>
        <span className={styles.value}>{product.description}</span>
      </div>

      <div className={styles.detailRow}>
        <span className={styles.label}>Цена: </span>
        <span className={styles.value}>{product.price} ₽</span>
      </div>

      <div className={styles.detailRow}>
        <span className={styles.label}>Дата: </span>
        <span className={styles.value}>
          {new Date(created_at).toLocaleString()}
        </span>
      </div>

      <div className={styles.detailRow}>
        <span className={styles.label}>Статус: </span>
        <span className={styles.value}>{status}</span>
      </div>

      <button className={styles.button} onClick={() => navigate(`/chat/${id}`)}>
        Написать в чат
      </button>
    </div>
  );
}
