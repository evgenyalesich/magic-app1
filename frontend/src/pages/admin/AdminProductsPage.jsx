// src/pages/admin/AdminProductsPage.jsx
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import styles from "./AdminProductsPage.module.css";

// 1. Импортируем хук useMe
import { useMe } from "../../api/auth";
import {
  fetchAdminProducts,
  updateAdminProduct,
  deleteAdminProduct,
} from "../../api/admin";

/* превращаем 'uploads/1.jpg' → 'https://api/…/uploads/1.jpg' */
const API_BASE = import.meta.env.VITE_API_URL || "";
const fullImageUrl = (path) => {
  if (!path) return "/img/placeholder.webp";
  if (path.startsWith("http")) return path;
  return `${API_BASE.replace(/\/+$/, "")}/${path.replace(/^\/+/, "")}`;
};

export default function AdminProductsPage() {
  /* ───────── state ───────── */
  const [products, setProducts] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    image_url: "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 2. Получаем статус авторизации
  const { isSuccess: isUserReady, isLoading: isUserLoading } = useMe();

  /* ───── загрузка списка ───── */
  // 3. Запускаем загрузку только после проверки пользователя
  useEffect(() => {
    if (isUserReady) {
      loadProducts();
    }
  }, [isUserReady]); // 4. Добавляем зависимость

  async function loadProducts() {
    try {
      setLoading(true);
      setProducts(await fetchAdminProducts());
    } catch (e) {
      console.error(e);
      setError("Не удалось загрузить товары");
    } finally {
      setLoading(false);
    }
  }

  /* ───── редактирование ───── */
  const startEdit = (p) => {
    setEditingId(p.id);
    setFormData({
      title: p.title || "",
      description: p.description || "",
      price: p.price || "",
      image_url: p.image_url || "",
    });
  };
  const cancelEdit = () => setEditingId(null);

  const handleChange = (e) =>
    setFormData((f) => ({ ...f, [e.target.name]: e.target.value }));

  const saveEdit = async (id) => {
    try {
      await updateAdminProduct(id, formData);
      toast.success("Сохранено");
      setEditingId(null);
      loadProducts();
    } catch (e) {
      toast.error(e.message || "Не удалось сохранить");
    }
  };

  /* ───── удаление ───── */
  const handleDelete = async (id) => {
    if (!window.confirm("Удалить товар?")) return;
    try {
      await deleteAdminProduct(id);
      setProducts((ps) => ps.filter((p) => p.id !== id));
      toast.success("Удалено");
    } catch (e) {
      toast.error(e.message || "Ошибка удаления");
    }
  };

  /* ───── UI-состояния ───── */
  // 5. Добавляем UI-состояние для проверки доступа
  if (isUserLoading)
    return <div className={styles.placeholder}>Проверка доступа…</div>;
  if (loading)
    return <div className={styles.placeholder}>Загрузка товаров…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;
  if (!products.length)
    return <div className={styles.placeholder}>Товаров нет</div>;

  /* ───── render ───── */
  return (
    <div className={styles.grid}>
      {products.map((p) =>
        editingId === p.id ? (
          /* ——— ФОРМА РЕДАКТИРОВАНИЯ ——— */
          <div key={p.id} className={styles.card}>
            <div className={styles.editForm}>
              {["title", "price", "image_url", "description"].map((field) =>
                field !== "description" ? (
                  <div key={field} className={styles.formGroup}>
                    <label className={styles.formLabel}>
                      {field === "title"
                        ? "Название"
                        : field === "price"
                          ? "Цена (₽)"
                          : "URL картинки"}
                    </label>
                    <input
                      className={styles.formInput}
                      name={field}
                      type={field === "price" ? "number" : "text"}
                      value={formData[field]}
                      onChange={handleChange}
                    />
                  </div>
                ) : (
                  <div key={field} className={styles.formGroup}>
                    <label className={styles.formLabel}>Описание</label>
                    <textarea
                      className={styles.formTextarea}
                      name="description"
                      value={formData.description}
                      onChange={handleChange}
                      rows="3"
                    />
                  </div>
                ),
              )}

              {formData.image_url && (
                <div className={styles.imagePreview}>
                  <img src={fullImageUrl(formData.image_url)} alt="preview" />
                </div>
              )}

              <div className={styles.formActions}>
                <button
                  className={styles.saveButton}
                  onClick={() => saveEdit(p.id)}
                >
                  💾 Сохранить
                </button>
                <button className={styles.cancelButton} onClick={cancelEdit}>
                  ❌ Отмена
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* ——— ОБЫЧНАЯ КАРТОЧКА ——— */
          <div key={p.id} className={styles.card}>
            <div className={styles.cardHeader}>
              {p.image_url ? (
                <img
                  src={fullImageUrl(p.image_url)}
                  alt={p.title}
                  className={styles.cardImage}
                  onError={(e) =>
                    (e.currentTarget.src = "/img/placeholder.webp")
                  }
                />
              ) : (
                <div className={styles.imagePlaceholder}>📷</div>
              )}
            </div>

            <div className={styles.cardContent}>
              <h3 className={styles.cardTitle}>{p.title || "Без названия"}</h3>
              <p className={styles.cardCategory}>
                {p.description || "Без описания"}
              </p>

              <div className={styles.cardMeta}>
                <span className={styles.price}>
                  {p.price ? `${p.price} ₽` : "Не указана"}
                </span>
                <span className={styles.rating}>{p.id}</span>
              </div>

              {/* ——— КНОПКИ СНИЗУ ——— */}
              <div className={styles.cardButtons}>
                <button
                  className={styles.editCardBtn}
                  onClick={() => startEdit(p)}
                >
                  ✎ Редактировать
                </button>
                <button
                  className={styles.deleteCardBtn}
                  onClick={() => handleDelete(p.id)}
                >
                  🗑 Удалить
                </button>
              </div>
            </div>
          </div>
        ),
      )}
    </div>
  );
}
