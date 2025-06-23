// src/pages/AdminProductsPage.jsx
import React, { useEffect, useState } from "react";
import styles from "./AdminProductsPage.module.css";
import {
  fetchAdminProducts,
  updateAdminProduct,
  deleteAdminProduct,
} from "../../api/admin";

export default function AdminProductsPage() {
  const [products, setProducts] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    image_url: "",
    // category_id: ""  // если нужна смена категории
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadProducts();
  }, []);

  async function loadProducts() {
    setLoading(true);
    setError("");
    try {
      const data = await fetchAdminProducts();
      setProducts(data);
    } catch (err) {
      console.error("Ошибка при загрузке товаров:", err);
      setError("Не удалось загрузить товары");
    } finally {
      setLoading(false);
    }
  }

  function startEdit(p) {
    setEditingId(p.id);
    setFormData({
      title: p.title,
      description: p.description,
      price: p.price,
      image_url: p.image_url,
      // category_id: p.category_id || ""
    });
  }

  function cancelEdit() {
    setEditingId(null);
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((f) => ({ ...f, [name]: value }));
  }

  async function saveEdit(id) {
    try {
      await updateAdminProduct(id, formData);
      setEditingId(null);
      await loadProducts();
      alert("Товар успешно обновлён");
    } catch (err) {
      console.error("Ошибка при сохранении товара:", err);
      alert("Не удалось сохранить изменения: " + err.message);
    }
  }

  async function handleDelete(id) {
    // безопасный confirm: если окно поддерживается — спросим, иначе удаляем сразу
    let ok = true;
    if (typeof window.confirm === "function") {
      ok = window.confirm("Точно удалить?");
    }
    if (!ok) return;

    try {
      const { id: deletedId } = await deleteAdminProduct(id);
      setProducts((ps) => ps.filter((p) => p.id !== deletedId));
      alert("Товар удалён");
    } catch (err) {
      console.error("Ошибка при удалении товара:", err);
      alert("Не удалось удалить товар: " + err.message);
    }
  }

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;

  return (
    <div className={styles.grid}>
      {products.map((p) => (
        <div key={p.id} className={styles.card}>
          {editingId === p.id ? (
            <div className={styles.editForm}>
              <input
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Название"
              />
              <input
                name="price"
                type="number"
                value={formData.price}
                onChange={handleChange}
                placeholder="Цена"
              />
              <input
                name="image_url"
                value={formData.image_url}
                onChange={handleChange}
                placeholder="URL картинки"
              />
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Описание"
              />
              {/* если нужны ещё поля, например категория */}
              {/* <input
                name="category_id"
                type="number"
                value={formData.category_id}
                onChange={handleChange}
                placeholder="ID категории"
              /> */}
              <div className={styles.buttons}>
                <button type="button" onClick={() => saveEdit(p.id)}>
                  Сохранить
                </button>
                <button type="button" onClick={cancelEdit}>
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <>
              <img
                src={p.image_url}
                alt={p.title}
                className={styles.cardImage}
              />
              <h3 className={styles.title}>{p.title}</h3>
              <p className={styles.description}>{p.description}</p>
              <div className={styles.footer}>
                <span className={styles.price}>{p.price} ₽</span>
                <div className={styles.buttons}>
                  <button
                    type="button"
                    className={styles.button}
                    onClick={() => startEdit(p)}
                  >
                    Редактировать
                  </button>
                  <button
                    type="button"
                    className={styles.deleteButton}
                    onClick={() => handleDelete(p.id)}
                  >
                    Удалить
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
