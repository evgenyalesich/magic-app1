// src/pages/CatalogPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { fetchProducts } from "../api/products";
import { initPayment, payWithFrikassa } from "../api/payments";

import styles from "./CatalogPage.module.css";

/** FAQ-курс из Telegram: 1 ⭐ ≈ 2.015 ₽ */
const STAR_RATE = 2.015;

export default function CatalogPage() {
  /* ----------------------------- state ---------------------------------- */
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [processingId, setProcessingId] = useState(null);

  /** Состояние модалки выбора оплаты */
  const [modal, setModal] = useState({
    open: false,
    orderId: null,
    invoice: null, // ← строка-ссылка
    productId: null,
  });

  const navigate = useNavigate();

  /* ---------------------- загрузка каталога ----------------------------- */
  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setItems(await fetchProducts());
      } catch {
        setError("Не удалось загрузить товары");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  /* ----------------------------- «Купить» ------------------------------- */
  const handleBuy = async (productId) => {
    setProcessingId(productId);
    try {
      // backend → { order_id, invoice }  (invoice — строка URL)
      const { order_id, invoice } = await initPayment(productId);
      setModal({ open: true, orderId: order_id, invoice, productId });
    } catch (err) {
      console.error(err);
      toast.error("Ошибка при создании заказа: " + err.message);
    } finally {
      setProcessingId(null);
    }
  };

  /* ---------- оплата звёздами через Telegram.WebApp.openInvoice --------- */
  const handlePayStars = () => {
    if (!modal.invoice) return;
    setProcessingId(modal.orderId);

    const link = modal.invoice; // ссылка-инвойс

    try {
      if (window?.Telegram?.WebApp?.openInvoice) {
        window.Telegram.WebApp.openInvoice(link, (status) => {
          if (status === "paid") {
            toast.success("Оплата прошла!");
            navigate(`/messages/${modal.orderId}`);
          } else if (status === "failed") {
            toast.error("Платёж не прошёл");
          }
        });
      } else {
        // fallback — открываем в новой вкладке
        window.open(link, "_blank");
        toast("Счёт открыт в новой вкладке");
        setTimeout(() => navigate(`/messages/${modal.orderId}`), 2500);
      }

      setModal((m) => ({ ...m, open: false }));
    } catch (err) {
      console.error(err);
      toast.error("Не удалось открыть счёт: " + err.message);
      setProcessingId(null);
    }
  };

  /* ------------------------- оплата через Frikassa ---------------------- */
  const handlePayFrikassa = async () => {
    setProcessingId(modal.orderId);
    try {
      await payWithFrikassa(modal.orderId);
      toast.success("Платёж через Frikassa инициирован!");
      setModal((m) => ({ ...m, open: false }));
      navigate(`/messages/${modal.orderId}`);
    } catch (err) {
      toast.error(err.message || "Frikassa ещё не настроена");
    } finally {
      setProcessingId(null);
    }
  };

  /* ------------------------------ UI ------------------------------------ */
  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!items.length)
    return <div className={styles.placeholder}>Товаров пока нет</div>;

  const currentProduct =
    modal.productId !== null
      ? items.find((i) => i.id === modal.productId)
      : null;

  const starsCost = currentProduct
    ? Math.ceil(currentProduct.price / STAR_RATE)
    : 0;

  return (
    <div className={styles.container}>
      {/* ----------------------- карточки товаров ----------------------- */}
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

      {/* ---------------- модальное окно выбора оплаты ------------------ */}
      {modal.open && (
        <div
          className={styles.modalOverlay}
          onClick={() => setModal((m) => ({ ...m, open: false }))}
        >
          <div
            className={styles.modal}
            onClick={(e) => e.stopPropagation()} // стопим "прокол" overlay
          >
            <h3>Выберите способ оплаты</h3>

            <div className={styles.modalButtons}>
              {modal.invoice && (
                <button
                  className={styles.starsButton}
                  disabled={processingId === modal.orderId}
                  onClick={handlePayStars}
                >
                  ⭐ Оплатить {starsCost} ⭐
                </button>
              )}

              <button
                className={styles.frikassaButton}
                disabled={processingId === modal.orderId}
                onClick={handlePayFrikassa}
              >
                Оплатить Frikassa
              </button>
            </div>

            <button
              className={styles.closeModal}
              onClick={() => setModal((m) => ({ ...m, open: false }))}
            >
              Отмена
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
