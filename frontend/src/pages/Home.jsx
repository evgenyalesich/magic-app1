// frontend/src/pages/Home.jsx
import React from "react";
import styles from "./Home.module.css";

export default function Home() {
  return (
    <div className={styles.grid}>
      {/* ⏳ позже сюда придут <ServiceCard/>, пока просто текст */}
      <div className={styles.placeholder}>Каталог загружается…</div>
    </div>
  );
}
