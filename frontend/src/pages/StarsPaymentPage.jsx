import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiClient } from "../api/client";
import styles from "./StarsPaymentPage.module.css";

export default function StarsPaymentPage() {
  const { productId } = useParams();
  const [stars, setStars] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleStarsPay = async () => {
    if (!stars) return setError("Введите количество звёзд");
    try {
      // сначала создаём заказ (по тому же API)
      const { data: order } = await apiClient.post("/payments", {
        product_id: +productId,
        quantity: 1,
      });
      // потом списываем звёзды
      await apiClient.post("/payments/stars", {
        order_id: order.id,
        stars: +stars,
      });
      // и сразу в чат
      navigate(`/chats/${order.id}`);
    } catch {
      setError("Не удалось списать звёзды");
    }
  };

  return (
    <div className={styles.page}>
      <h1>Оплата звёздами</h1>
      {error && <div className={styles.error}>{error}</div>}
      <input
        type="number"
        value={stars}
        onChange={(e) => setStars(e.target.value)}
        placeholder="Сколько звёзд потратить?"
        className={styles.input}
      />
      <button onClick={handleStarsPay} className={styles.payBtn}>
        Списать звёзды
      </button>
    </div>
  );
}
