import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";

import { apiClient } from "../api/client";
import { initPayment } from "../api/payments";

import styles from "./StarsPaymentPage.module.css";

export default function StarsPaymentPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);

  const handleStarsPay = async () => {
    if (busy) return;
    try {
      setBusy(true);

      /* 1. создаём заказ и получаем invoice */
      const { order_id, invoice } = await initPayment(+productId);

      /* 2. открываем окно оплаты у Telegram */
      await window.Telegram.WebApp.openInvoice(invoice);

      /* 3. простейший polling – смотрим, когда заказ станет paid */
      const poll = setInterval(async () => {
        const { data: order } = await apiClient.get(`/orders/${order_id}`);
        if (order.status === "paid") {
          clearInterval(poll);
          toast.success("Оплачено звёздами!");
          navigate(`/chats/${order_id}`);
        }
      }, 3000);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={styles.page}>
      <h1>Оплата звёздами</h1>

      <button
        onClick={handleStarsPay}
        className={styles.payBtn}
        disabled={busy}
      >
        {busy ? "Ожидаем оплату…" : "Оплатить через ⭐ Telegram"}
      </button>
    </div>
  );
}
