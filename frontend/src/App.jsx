// src/App.jsx
import React, { useEffect } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { useMe } from "./api/auth";
import LoginPage from "./pages/LoginPage";
import Home from "./pages/Home";
import AdminLayout from "./pages/AdminLayout";

// Admin sub-pages
import AdminProductsPage from "./pages/admin/AdminProductsPage";
import NewProductPage from "./pages/admin/NewProductPage";
import AdminMessagesPage from "./pages/admin/AdminMessagesPage";
import AdminReportPage from "./pages/admin/AdminReportPage";

import { CartButton } from "./components/CartBadge";
import styles from "./App.module.css";
import "./index.css";

function Shell() {
  const { data: me, isLoading } = useMe();
  const navigate = useNavigate();

  // при заходе на /admin сразу редиректим на /admin/products
  useEffect(() => {
    if (!isLoading && me?.is_admin && window.location.pathname === "/admin") {
      navigate("products", { replace: true });
    }
  }, [me, isLoading, navigate]);

  if (isLoading) return <div className={styles.loading}>Загрузка…</div>;
  if (!me) return <Navigate to="/login" replace />;

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <a href="/" className={styles.logo}>
          🔮 Magic App
        </a>
        <div className={styles.controls}>
          {me.is_admin && (
            <a href="/admin" className={styles.adminLink}>
              Admin
            </a>
          )}
          <CartButton />
        </div>
      </header>

      <main className={styles.main}>
        <Routes>
          {/* Пользовательская главная */}
          <Route path="/" element={<Home />} />

          {/* Админская секция */}
          {me.is_admin && (
            <Route path="admin/*" element={<AdminLayout />}>
              {/* /admin → сразу на список */}
              <Route index element={<Navigate to="products" replace />} />

              {/* /admin/products */}
              <Route path="products" element={<AdminProductsPage />} />

              {/* /admin/products/new */}
              <Route path="products/new" element={<NewProductPage />} />

              {/* /admin/messages */}
              <Route path="messages" element={<AdminMessagesPage />} />

              {/* /admin/report */}
              <Route path="report" element={<AdminReportPage />} />
            </Route>
          )}

          {/* всё остальное — на главную */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function InitDataRedirector() {
  const { data: me, isLoading } = useMe();
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoading) return;
    if (!me && window.Telegram?.WebApp?.initData) {
      navigate(
        `/login?initData=${encodeURIComponent(
          window.Telegram.WebApp.initData,
        )}`,
        { replace: true },
      );
    }
  }, [me, isLoading, navigate]);

  return null;
}

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {/* перенаправление из телеги */}
        <InitDataRedirector />

        {/* собственно всё остальное */}
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<Shell />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
