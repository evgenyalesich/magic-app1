// src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { useMe } from "./api/auth";
import LoginPage from "./pages/LoginPage";
import Home from "./pages/Home";
import Admin from "./pages/Admin";
import { CartButton } from "./components/CartBadge";
import styles from "./App.module.css";
import "./index.css";

function Shell() {
  const { data: me, isLoading } = useMe();

  if (isLoading) return <div className={styles.loading}>Загрузка…</div>;
  if (!me) return <Navigate to="/login" replace />;

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Link to="/" className={styles.logo}>
          🔮 Magic App
        </Link>
        <div className={styles.controls}>
          {me.is_admin && (
            <Link to="/admin" className={styles.adminLink}>
              Admin
            </Link>
          )}
          <CartButton />
        </div>
      </header>
      <main className={styles.main}>
        <Routes>
          <Route path="/" element={<Home />} />
          {me.is_admin && <Route path="/admin" element={<Admin />} />}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<Shell />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
