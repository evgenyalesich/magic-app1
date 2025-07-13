import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";

// 1. Импортируем хук useMe
import { useMe } from "../api/auth";
import { createOrderForStars } from "../api/payments";

import styles from "./StarsPaymentPage.module.css";

export default function StarsPaymentPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);

  // 2. Получаем статус загрузки пользователя
  const { isSuccess: isUserLoaded, isLoading: isUserLoading } = useMe();

  const handleStarsPay = async () => {
    // Добавим дополнительную проверку на всякий случай
    if (busy || !isUserLoaded) return;
    setBusy(true);

    try {
      // 1. создаём pending-заказ и получаем { order_id, invoice }
      const { order_id, invoice } = await createOrderForStars(+productId);

      // 2. подписываемся на WebApp-событие успешной оплаты
      window.Telegram.WebApp.onEvent("payment_successful", () => {
        toast.success("Оплата звёздами прошла успешно!");
        // 3. в момент подтверждения платёжа — сразу в чат
        navigate(`/messages/${order_id}`);
      });

      // 4. поехали — открываем окно оплаты
      await window.Telegram.WebApp.openInvoice(invoice);
    } catch (err) {
      console.error("Ошибка оплаты звёздами:", err);
      toast.error(err.message || "Не удалось оплатить звёздами");
      setBusy(false);
    }
    // busy останется true, пока не придёт событие payment_successful
  };

  // 3. Функция для определения текста на кнопке
  const getButtonText = () => {
    if (isUserLoading) return "Проверка сессии…";
    if (busy) return "Ожидаем подтверждения…";
    return "Оплатить через ⭐ Telegram";
  };

  return (
    <div className={styles.page}>
      <h1>Оплата звёздами</h1>
      <button
        onClick={handleStarsPay}
        className={styles.payBtn}
        // 4. Блокируем кнопку, если идёт проверка пользователя или оплата
        disabled={busy || isUserLoading || !isUserLoaded}
      >
        {getButtonText()}
      </button>
    </div>
  );
}
