// src/pages/AdminHomePage.jsx
import React from "react";
import { Link } from "react-router-dom";
import styles from "./AdminHomePage.module.css";

export default function AdminHomePage() {
  return (
    <div className={styles.container}>
      <h1 className={styles.header}>Magic App — Admin</h1>
      <nav className={styles.nav}>
        <Link to="/admin/products">Товары</Link>
        <Link to="/admin/products/new">Добавить услугу</Link>
        <Link to="/admin/messages">Сообщения</Link>
        <Link to="/admin/report">Отчёт / Статистика</Link>
      </nav>
      {/* Ниже можно добавить например дашборд или превью списка */}
    </div>
  );
}
