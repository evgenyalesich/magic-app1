// src/pages/AdminLayout.jsx
import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import styles from "./AdminLayout.module.css";

export default function AdminLayout() {
  return (
    <div className={styles.adminShell}>
      <h1 className={styles.header}>Magic App — Admin</h1>

      <nav className={styles.toolbar}>
        <NavLink
          to="products"
          className={({ isActive }) =>
            `${styles.link} ${isActive ? styles.active : ""}`.trim()
          }
        >
          Товары
        </NavLink>

        <NavLink
          to="products/new"
          className={({ isActive }) =>
            `${styles.link} ${isActive ? styles.active : ""}`.trim()
          }
        >
          Добавить услугу
        </NavLink>

        <NavLink
          to="messages"
          className={({ isActive }) =>
            `${styles.link} ${isActive ? styles.active : ""}`.trim()
          }
        >
          Сообщения
        </NavLink>

        <NavLink
          to="report"
          className={({ isActive }) =>
            `${styles.link} ${isActive ? styles.active : ""}`.trim()
          }
        >
          Отчёт / Статистика
        </NavLink>
      </nav>

      {/* Вот он – ваш “viewport” для всех вложенных админ-страниц */}
      <section className={styles.content}>
        <Outlet />
      </section>
    </div>
  );
}
