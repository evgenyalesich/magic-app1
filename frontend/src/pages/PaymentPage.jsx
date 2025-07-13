import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";

// 1. Импортируем хук useMe
import { useMe } from "../api/auth";
import { apiClient } from "../api/client";
import { createOrderForStars, payWithFrikassa } from "../api/payments";
import { pollOrderStatus } from "../utils/polling";

import styles from "./PaymentPage.module.css";

const STAR_RATE = 2.015;

export default function PaymentPage() {
  const { productId } = useParams();
  const navigate = useNavigate();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  // 2. Получаем статус загрузки пользователя
  const { isSuccess: isUserLoaded, isLoading: isUserLoading } = useMe();

  /* ─────────── загрузка товара ─────────── */
  useEffect(() => {
    // Этот запрос можно не блокировать, так как информация о товаре, скорее всего, публичная
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

  const waitForPaymentAndGoToChat = async (orderId) => {
    toast.loading("Ожидаем подтверждения оплаты...");
    const isPaid = await pollOrderStatus(orderId);
    toast.dismiss();

    if (isPaid) {
      goToChat(orderId);
    } else {
      setBusy(false);
      navigate(`/orders/${orderId}`);
    }
  };

  /* ─────────── оплата картой (Frikassa) ─────────── */
  const handleCardPay = async () => {
    if (!product || busy) return;
    setBusy(true);
    try {
      const { order_id } = await createOrderForStars(product.id);
      const { redirect_url } = await payWithFrikassa(order_id);
      window.open(redirect_url, "_blank", "noopener,noreferrer");
      await waitForPaymentAndGoToChat(order_id);
    } catch (err) {
      toast.error(err.message || "Ошибка оплаты картой");
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
      const { order_id, invoice } = await createOrderForStars(product.id);
      if (!invoice) throw new Error("Сервер не вернул ссылку на счёт");
      const open = window.Telegram.WebApp.openInvoice ?? window.open;
      open(invoice, "_blank", "noopener,noreferrer");
      await waitForPaymentAndGoToChat(order_id);
    } catch (err) {
      toast.error(err.message || "Ошибка при оплате ⭐");
      setBusy(false);
    }
  };

  /* ─────────────────────────── UI ─────────────────────────── */
  // Пока идёт проверка пользователя, показываем статус
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка сессии…</div>;

  if (loading)
    return <div className={styles.placeholder}>Загрузка товара…</div>;
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
          // 3. Блокируем кнопку, пока пользователь не авторизован
          disabled={busy || !isUserLoaded}
        >
          Оплатить картой
        </button>

        <button
          onClick={handleStarsPay}
          className={styles.starsBtn}
          // 3. Блокируем кнопку, пока пользователь не авторизован
          disabled={busy || !isUserLoaded}
        >
          Оплатить {starsPrice} ⭐
        </button>
      </div>
    </div>
  );
}
