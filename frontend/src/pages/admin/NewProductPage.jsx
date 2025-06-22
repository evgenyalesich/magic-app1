// src/pages/admin/NewProductPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./NewProductPage.module.css";
import { createAdminProduct } from "../../api/admin";

export default function NewProductPage() {
  const [form, setForm] = useState({
    title: "",
    description: "",
    price: "",
    image_url: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await createAdminProduct(form);
      alert("Услуга успешно добавлена");
      navigate("/admin/products");
    } catch (err) {
      console.error(err);
      setError("Не удалось добавить услугу: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <h2 className={styles.heading}>Новая услуга</h2>

        {error && <div className={styles.error}>{error}</div>}

        <label className={styles.label}>
          Название
          <input
            name="title"
            className={styles.input}
            value={form.title}
            onChange={handleChange}
            required
          />
        </label>

        <label className={styles.label}>
          Описание
          <textarea
            name="description"
            className={styles.textarea}
            value={form.description}
            onChange={handleChange}
            required
          />
        </label>

        <label className={styles.label}>
          Цена (₽)
          <input
            name="price"
            type="number"
            className={styles.input}
            value={form.price}
            onChange={handleChange}
            required
          />
        </label>

        <label className={styles.label}>
          URL картинки
          <input
            name="image_url"
            className={styles.input}
            value={form.image_url}
            onChange={handleChange}
            required
          />
        </label>

        <div className={styles.buttons}>
          <button
            type="submit"
            className={styles.submitButton}
            disabled={submitting}
          >
            {submitting ? "Сохраняем…" : "Добавить"}
          </button>
          <button
            type="button"
            className={styles.cancelButton}
            onClick={() => navigate("/admin/products")}
            disabled={submitting}
          >
            Отмена
          </button>
        </div>
      </form>
    </div>
  );
}
