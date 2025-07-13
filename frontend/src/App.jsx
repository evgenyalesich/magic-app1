import React, { useEffect, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
  Link,
} from "react-router-dom";
// 👇 ИМПОРТИРУЕМ useQueryClient ДЛЯ УПРАВЛЕНИЯ КЭШЕМ
import {
  QueryClient,
  QueryClientProvider,
  useQueryClient,
} from "@tanstack/react-query";

import { useMe } from "./api/auth";
import LoginPage from "./pages/LoginPage";
import CatalogPage from "./pages/CatalogPage";
import ChatListPage from "./pages/ChatListPage";
import ChatWindowPage from "./pages/ChatWindowPage";
import PaymentPage from "./pages/PaymentPage";
import StarsPaymentPage from "./pages/StarsPaymentPage";
import PurchaseHistoryPage from "./pages/PurchaseHistoryPage";
import OrderConfirmationPage from "./pages/OrderConfirmation";

/* —— Админка —— */
import AdminLayout from "./pages/AdminLayout";
import AdminProductsPage from "./pages/admin/AdminProductsPage";
import NewProductPage from "./pages/admin/NewProductPage";
import AdminChatPage from "./pages/admin/AdminChatPage";
import AdminReportPage from "./pages/admin/AdminReportPage";
import AdminChatListPage from "./pages/admin/AdminChatList";

import SideMenu from "./components/SideMenu";

import styles from "./App.module.css";
import "./index.css";

function Shell() {
  const { data: me, isLoading } = useMe();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  // 👇 ПОЛУЧАЕМ ДОСТУП К КЛИЕНТУ REACT QUERY
  const queryClient = useQueryClient();

  // ✅ ЭФФЕКТ ДЛЯ ОЧИСТКИ КЭША ПРИ ВЫХОДЕ ИЗ СИСТЕМЫ
  useEffect(() => {
    // Этот эффект следит за состоянием пользователя.
    // Если пользователь не авторизован (!me), мы очищаем весь кэш.
    // Это гарантирует, что при входе нового пользователя все данные
    // (чаты, покупки) будут загружены с сервера заново и не произойдет утечки
    // данных от предыдущей сессии.
    if (!isLoading && !me) {
      queryClient.clear();
    }
  }, [me, isLoading, queryClient]);

  /* —— если админ открыл /admin — редирект на /admin/products —— */
  useEffect(() => {
    if (!isLoading && me?.is_admin && window.location.pathname === "/admin") {
      navigate("products", { replace: true });
    }
  }, [me, isLoading, navigate]);

  if (isLoading) return <div className={styles.loading}>Загрузка…</div>;

  // Эта проверка теперь сработает ПОСЛЕ того, как кэш будет очищен
  if (!me) return <Navigate to="/login" replace />;

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <button
          className={styles.menuButton}
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Открыть меню"
        >
          ☰
        </button>
        <Link to="/" className={styles.logo}>
          🔮 Зеркало Судьбы
        </Link>
        <div className={styles.controls}>
          {me.is_admin && (
            <Link to="/admin" className={styles.adminLink}>
              Admin
            </Link>
          )}
        </div>
      </header>

      <SideMenu open={menuOpen} onClose={() => setMenuOpen(false)} />

      <main className={styles.main} onClick={() => setMenuOpen(false)}>
        <Routes>
          {/* корень → каталог */}
          <Route path="/" element={<Navigate to="services" replace />} />

          {/* —— публичная часть —— */}
          <Route path="services" element={<CatalogPage />} />

          {/* 👇 ВСЕ МАРШРУТЫ, СВЯЗАННЫЕ С ОПЛАТОЙ, ТЕПЕРЬ ЗДЕСЬ */}
          <Route path="payments/:productId" element={<PaymentPage />} />
          <Route
            path="payments/stars/:productId"
            element={<StarsPaymentPage />}
          />
          <Route path="orders/:orderId" element={<OrderConfirmationPage />} />

          {/* —— чаты и история —— */}
          <Route path="messages" element={<ChatListPage />} />
          <Route path="messages/:orderId" element={<ChatWindowPage />} />
          <Route path="purchases" element={<PurchaseHistoryPage />} />

          {/* —— админка —— */}
          {me.is_admin && (
            <Route path="admin/*" element={<AdminLayout />}>
              <Route index element={<Navigate to="products" replace />} />
              <Route path="products" element={<AdminProductsPage />} />
              <Route path="products/new" element={<NewProductPage />} />
              <Route path="messages" element={<AdminChatListPage />} />
              <Route path="messages/:orderId" element={<AdminChatPage />} />
              <Route path="report" element={<AdminReportPage />} />
            </Route>
          )}

          {/* любой прочий URL → в каталог */}
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
        <InitDataRedirector />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          {/* 👇 Упрощённая структура: Shell обрабатывает все авторизованные маршруты */}
          <Route path="/*" element={<Shell />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
