// src/pages/Admin.jsx
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { fetchProducts, createProduct } from "../api/products";

import styles from "./Admin.module.css";

export default function Admin() {
  const qc = useQueryClient();

  // 1) загрузка списка
  const { data: products = [], isLoading } = useQuery({
    queryKey: ["admin-products"],
    queryFn: fetchProducts,
  });

  // 2) мутация добавления
  const { mutateAsync: addProduct, isLoading: isSaving } = useMutation({
    mutationFn: createProduct,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-products"] });
    },
  });

  // локальные стейты формы
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [imageUrl, setImageUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await addProduct({
      name,
      description,
      price: Number(price),
      image: imageUrl,
    });
    // сброс формы
    setName("");
    setDescription("");
    setPrice("");
    setImageUrl("");
  };

  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>Админка: Управление товарами</h1>

      {/* Форма добавления */}
      <form onSubmit={handleSubmit} className={styles.form}>
        <h2 className={styles.subheading}>Добавить новый товар</h2>

        <div className={styles.field}>
          <label className={styles.label}>Название</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className={styles.input}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Описание</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            className={styles.textarea}
          />
        </div>

        <div className={styles.row}>
          <div className={styles.field}>
            <label className={styles.label}>Цена (₽)</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
              className={styles.input}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>URL картинки</label>
            <input
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              required
              className={styles.input}
            />
          </div>
        </div>

        <button type="submit" disabled={isSaving} className={styles.button}>
          {isSaving ? "Сохраняем…" : "Добавить товар"}
        </button>
      </form>

      {/* Список товаров */}
      <div className={styles.grid}>
        {isLoading ? (
          <p>Загрузка…</p>
        ) : (
          products.map((p) => (
            <div key={p.id} className={styles.card}>
              <img src={p.image} alt={p.name} className={styles.cardImage} />
              <div className={styles.cardContent}>
                <h3 className={styles.cardTitle}>{p.name}</h3>
                <p className={styles.cardDesc}>{p.description}</p>
                <div className={styles.cardFooter}>
                  <span className={styles.cardPrice}>{p.price} ₽</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
