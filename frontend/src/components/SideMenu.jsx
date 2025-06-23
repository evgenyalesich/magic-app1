// src/components/SideMenu.jsx
import React from "react";
import { Link } from "react-router-dom";
import styles from "./SideMenu.module.css";

export default function SideMenu({ open, onClose }) {
  return (
    <>
      <div
        className={`${styles.overlay} ${open ? styles.show : ""}`}
        onClick={onClose}
      />
      <nav className={`${styles.menu} ${open ? styles.open : ""}`}>
        <ul>
          <li>
            {/* Вместо "/services" ведём на "/catalog" */}
            <Link to="/catalog" onClick={onClose}>
              Каталог услуг
            </Link>
          </li>
          <li>
            <Link to="/orders/history" onClick={onClose}>
              История заказов
            </Link>
          </li>
          <li>
            <Link to="/messages" onClick={onClose}>
              Сообщения
            </Link>
          </li>
        </ul>
      </nav>
    </>
  );
}
