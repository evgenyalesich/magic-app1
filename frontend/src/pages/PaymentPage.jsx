import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";

import { apiClient } from "../api/client";
import { initPayment, payWithFrikassa } from "../api/payments";

import styles from "./PaymentPage.module.css";

/** приближённый курс из FAQ Telegram: 1 ⭐ ≈ 2.015 ₽ */
const STAR_RATE = 2.015;

export default function PaymentPage() {
  const { productId } = useParams();
  const navigate = useNavigate();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  /* ─────────── загрузка товара ─────────── */
  useEffect(() => {
    (async () => {
      try {
        const { data } = await apiClient.get(`/products/${productId}`);
        setProduct(data);
      } catch (err) {
        toast.error(err.message || "Не удалось загрузить товар");
      } finally {
        setLoading(false);
      }
    })();
  }, [productId]);

  /* ─────────── helper: переход в чат ─────────── */
  const goToChat = (orderId) => {
    navigate(`/messages/${orderId}`, {
      state: { productTitle: product.title },
    });
  };

  /* ─────────── оплата картой (Frikassa) ─────────── */
  const handleCardPay = async () => {
    if (!product || busy) return;
    setBusy(true);
    try {
      const { order_id } = await initPayment(product.id); // создаём pending-заказ
      const { redirect_url } = await payWithFrikassa(order_id); // получаем ссылку на форму
      window.open(redirect_url, "_blank", "noopener,noreferrer"); // открываем платёжку
      setTimeout(() => goToChat(order_id), 5_000); // через 5 с — в чат
    } catch (err) {
      toast.error(err.message || "Ошибка оплаты картой");
    } finally {
      setBusy(false);
    }
  };

  /* ─────────── оплата звёздами (Telegram Stars) ─────────── */
  const handleStarsPay = async () => {
    if (!product || busy) return;

    if (!window.Telegram?.WebApp) {
      toast.error("Откройте страницу внутри Telegram-бота, чтобы платить ⭐");
      return;
    }

    setBusy(true);
    try {
      const { order_id, invoice } = await initPayment(product.id); // invoice — строка-URL

      if (!invoice) throw new Error("Сервер не вернул ссылку на счёт");

      // если WebApp умеет openInvoice — используем; иначе обычное window.open
      const open = window.Telegram.WebApp.openInvoice ?? window.open;
      open(invoice, "_blank", "noopener,noreferrer");

      // даём WebApp + webhook-у время; потом переходим в чат
      setTimeout(() => goToChat(order_id), 2_500);
    } catch (err) {
      toast.error(err.message || "Ошибка при оплате ⭐");
    } finally {
      setBusy(false);
    }
  };

  /* ─────────────────────────── UI ─────────────────────────── */
  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (!product)
    return <div className={styles.placeholder}>Товар не найден</div>;

  const starsPrice = Math.ceil(product.price / STAR_RATE);

  return (
    <div className={styles.page}>
      <h1>Оплатить «{product.title}»</h1>
      <p>
        Цена: {product.price} ₽ / {starsPrice} ⭐
      </p>

      <div className={styles.buttons}>
        <button
          onClick={handleCardPay}
          className={styles.payBtn}
          disabled={busy}
        >
          Оплатить картой
        </button>

        <button
          onClick={handleStarsPay}
          className={styles.starsBtn}
          disabled={busy}
        >
          Оплатить {starsPrice} ⭐
        </button>
      </div>
    </div>
  );
}
