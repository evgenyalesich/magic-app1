// src/components/Layout.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom"; // или ваш роутер
import SideMenu from "./SideMenu";
import styles from "./Layout.module.css";

export default function Layout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen((open) => !open);
  const closeMenu = () => setMenuOpen(false);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <button
          className={styles.menuButton}
          onClick={toggleMenu}
          aria-label="Открыть меню"
        >
          ☰
        </button>
        <Link to="/" className={styles.logo}>
          🔮 Magic App
        </Link>
        <div className={styles.spacer} />
        <span className={styles.adminBadge}>Admin</span>
        <Link to="/cart" className={styles.cartButton} aria-label="Корзина">
          🛒
        </Link>
      </header>

      <SideMenu open={menuOpen} onClose={closeMenu} />

      <main className={styles.main} onClick={closeMenu}>
        {children}
      </main>
    </div>
  );
}
