// src/pages/CatalogPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchProducts } from "../api/products";
import { initPayment, payWithStars, payWithFrikassa } from "../api/payments";
import styles from "./CatalogPage.module.css";

export default function CatalogPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [processingId, setProcessingId] = useState(null);

  // состояние модалки теперь включает productId
  const [modal, setModal] = useState({
    open: false,
    orderId: null,
    options: [],
    productId: null,
  });

  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const products = await fetchProducts();
        setItems(products);
      } catch {
        setError("Не удалось загрузить товары");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Нажали «Купить» — инициируем оплату и открываем модалку с productId
  const handleBuy = async (productId) => {
    setProcessingId(productId);
    try {
      const { order_id, options } = await initPayment(productId);
      setModal({ open: true, orderId: order_id, options, productId });
    } catch (err) {
      console.error(err);
      alert("Ошибка при создании заказа: " + err.message);
    } finally {
      setProcessingId(null);
    }
  };

  const handlePayStars = async () => {
    setProcessingId(modal.orderId);
    try {
      await payWithStars(modal.orderId);
      setModal({ ...modal, open: false });
      navigate(`/messages?order_id=${modal.orderId}`);
    } catch (err) {
      console.error(err);
      alert("Ошибка при оплате звёздами: " + err.message);
    } finally {
      setProcessingId(null);
    }
  };

  const handlePayFrikassa = async () => {
    setProcessingId(modal.orderId);
    try {
      await payWithFrikassa(modal.orderId);
      alert("Платёж через Frikassa прошёл успешно!");
      setModal({ ...modal, open: false });
    } catch (err) {
      alert(err.message || "Frikassa ещё не настроена");
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!items.length)
    return <div className={styles.placeholder}>Товаров пока нет</div>;

  // находим текущий товар из списка и считаем стоимость в звёздах
  const currentProduct =
    modal.productId !== null
      ? items.find((item) => item.id === modal.productId)
      : null;
  const starsCost = currentProduct
    ? Math.ceil(currentProduct.price / 2.015)
    : 0;

  return (
    <div className={styles.container}>
      <div className={styles.grid}>
        {items.map((item) => (
          <div key={item.id} className={styles.card}>
            <img
              src={item.image_url}
              alt={item.title}
              className={styles.cardImage}
            />
            <div className={styles.cardContent}>
              <h2 className={styles.title}>{item.title}</h2>
              <p className={styles.description}>{item.description}</p>
              <div className={styles.footer}>
                <span className={styles.price}>{item.price} ₽</span>
                <button
                  className={styles.button}
                  disabled={processingId === item.id}
                  onClick={() => handleBuy(item.id)}
                >
                  {processingId === item.id ? "Обработка…" : "Купить"}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Модальное окно выбора способа оплаты */}
      {modal.open && (
        <div
          className={styles.modalOverlay}
          onClick={() => setModal({ ...modal, open: false })}
        >
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>Выберите способ оплаты</h3>
            <div className={styles.modalButtons}>
              {modal.options.includes("stars") && currentProduct && (
                <button
                  className={styles.starsButton}
                  disabled={processingId === modal.orderId}
                  onClick={handlePayStars}
                >
                  Оплатить {starsCost} ⭐ за {currentProduct.price} ₽
                </button>
              )}
              {modal.options.includes("frikassa") && (
                <button
                  className={styles.frikassaButton}
                  disabled={processingId === modal.orderId}
                  onClick={handlePayFrikassa}
                >
                  Оплатить Frikassa
                </button>
              )}
            </div>
            <button
              className={styles.closeModal}
              onClick={() => setModal({ ...modal, open: false })}
            >
              Отмена
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
