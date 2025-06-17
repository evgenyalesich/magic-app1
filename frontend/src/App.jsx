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
          <Route path="/" element={<Home />} />
          {me.is_admin && <Route path="/admin" element={<Admin />} />}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

// ❗️Компонент обёртка, проверяющая initData
function InitDataRedirector() {
  const navigate = useNavigate();

  useEffect(() => {
    const initData = window.Telegram?.WebApp?.initData;
    if (initData) {
      navigate(`/login?initData=${encodeURIComponent(initData)}`, {
        replace: true,
      });
    }
  }, [navigate]);

  return null; // ничего не рендерим
}

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <>
                <InitDataRedirector />
                <Shell />
              </>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
