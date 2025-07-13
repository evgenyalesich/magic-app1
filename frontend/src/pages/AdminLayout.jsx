import React from "react";
import { NavLink, Outlet, Navigate } from "react-router-dom";

// 1. Импортируем хук useMe для получения данных о пользователе
import { useMe } from "../api/auth";
import styles from "./AdminLayout.module.css";

export default function AdminLayout() {
  // 2. Получаем данные о текущем пользователе
  const { data: user, isLoading, isError } = useMe();

  // 3. Пока идёт проверка, показываем статус загрузки
  if (isLoading) {
    return <div className={styles.placeholder}>Проверка доступа…</div>;
  }

  // 4. Если произошла ошибка или у пользователя нет флага is_admin,
  //    показываем сообщение об ошибке доступа.
  if (isError || !user?.is_admin) {
    return (
      <div className={styles.placeholder}>
        <h1>🚫 Доступ запрещён</h1>
        <p>У вас нет прав для просмотра этого раздела.</p>
      </div>
    );
    // Альтернативный вариант: можно сделать редирект на главную страницу
    // return <Navigate to="/" replace />;
  }

  // 5. Если все проверки пройдены, пользователь — админ.
  //    Показываем интерфейс админки и вложенную страницу (`<Outlet />`).
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

      {/* Viewport для всех вложенных админ-страниц */}
      <section className={styles.content}>
        <Outlet />
      </section>
    </div>
  );
}
