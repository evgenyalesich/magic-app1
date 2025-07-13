// src/components/SideMenu.jsx
import React from "react";
import { Link } from "react-router-dom";
import styles from "./SideMenu.module.css";

/**
 * Боковое меню-бургер.
 *
 * props:
 *  • open   — boolean, открыто ли меню
 *  • onClose — функция, вызывается при клике по overlay или пункту меню
 */
export default function SideMenu({ open, onClose }) {
  return (
    <>
      {/* затемняющая подложка */}
      <div
        className={`${styles.overlay} ${open ? styles.show : ""}`}
        onClick={onClose}
      />

      {/* само выезжающее меню */}
      <nav className={`${styles.menu} ${open ? styles.open : ""}`}>
        <ul>
          <li>
            {/* каталог услуг: у нас маршрут /services */}
            <Link to="/services" onClick={onClose}>
              🛠️ Каталог услуг
            </Link>
          </li>

          <li>
            {/* новая страница истории покупок */}
            <Link to="/purchases" onClick={onClose}>
              🛍️ История покупок
            </Link>
          </li>

          <li>
            {/* список всех чатов / сообщений */}
            <Link to="/messages" onClick={onClose}>
              💬 Сообщения
            </Link>
          </li>
        </ul>
      </nav>
    </>
  );
}
