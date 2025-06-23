import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiClient } from "../api/client";
import { initPayment, payWithStars } from "../api/payments";
import { getProfile } from "../api/profile";
import toast from "react-hot-toast";
import styles from "./PaymentPage.module.css";

export default function PaymentPage() {
  const { productId } = useParams();

  // товар
  const [product, setProduct] = useState(null);
  const [loadingProduct, setLoadingProduct] = useState(true);

  // звёздный баланс
  const [stars, setStars] = useState(null);
  const [loadingStars, setLoadingStars] = useState(true);

  // флаг выполнения любого платежа (для дизейбла кнопок)
  const [busy, setBusy] = useState(false);

  const navigate = useNavigate();

  /** Загружаем описание продукта */
  useEffect(() => {
    setLoadingProduct(true);
    apiClient
      .get(`/products/${productId}`)
      .then(({ data }) => setProduct(data))
      .catch((err) => toast.error(err.message))
      .finally(() => setLoadingProduct(false));
  }, [productId]);

  /** Загружаем профиль, чтобы узнать баланс звёзд */
  useEffect(() => {
    setLoadingStars(true);
    getProfile()
      .then((profile) => setStars(profile.stars))
      .catch((err) => toast.error(err.message))
      .finally(() => setLoadingStars(false));
  }, []);

  /** Оплата картой (Frikassa остаётся как было) */
  const handleCardPay = async () => {
    try {
      setBusy(true);
      const { data: order } = await apiClient.post("/payments", {
        product_id: product.id,
        quantity: 1,
        price: product.price,
      });
      navigate(`/chats/${order.id}`);
    } finally {
      setBusy(false);
    }
  };

  /** Оплата звёздами */
  const handleStarsPay = async () => {
    if (!product) return;
    if (stars < product.starsPrice) return; // теоретическая защита на клиенте

    try {
      setBusy(true);
      // 1. создаём заказ (initPayment отвечает order_id)
      const { order_id } = await initPayment(product.id);
      // 2. пытаемся оплатить звёздами
      await payWithStars(order_id);
      toast.success("Оплачено звёздами!");
      navigate(`/chats/${order_id}`);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (loadingProduct || loadingStars) {
    return <div className={styles.placeholder}>Загрузка…</div>;
  }

  const enoughStars = stars >= product.starsPrice;

  return (
    <div className={styles.page}>
      <h1>Оплатить «{product.title}»</h1>
      <p>
        Цена: {product.price} ₽ / {product.starsPrice} ⭐
      </p>

      {/* КНОПКА КАРТЫ (остаётся как была) */}
      <button onClick={handleCardPay} className={styles.payBtn} disabled={busy}>
        Оплатить картой
      </button>

      {/* КНОПКА ЗВЁЗД */}
      {enoughStars ? (
        <button
          onClick={handleStarsPay}
          className={styles.starsBtn}
          disabled={busy}
        >
          Оплатить {product.starsPrice} ⭐
        </button>
      ) : (
        <button className={styles.starsBtnDisabled} disabled>
          Нужно {product.starsPrice} ⭐ (у вас {stars})
        </button>
      )}
    </div>
  );
}
