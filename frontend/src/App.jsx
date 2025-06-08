// frontend/src/App.jsx
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProductList from "./components/ProductList";
import ProductDetail from "./components/ProductDetail";
import ChatWindow from "./components/ChatWindow";
import { initTelegram, fetchCurrentUser } from "./telegram";
import "./App.css";

const queryClient = new QueryClient();

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      // внутри WebApp — логинимся через Telegram
      initTelegram()
        .catch(err => {
          console.error("Ошибка логина:", err);
        })
        .then(() => fetchCurrentUser())
        .then(profile => {
          if (profile) setUser(profile);
          else console.warn("Login succeeded but /me вернул null");
        });
      // тема
      const theme = tg.colorScheme;
      document.documentElement.classList.toggle("dark", theme === "dark");
    } else {
      // прямой заход — просто пробуем по кукам
      fetchCurrentUser().then(profile => {
        if (profile) setUser(profile);
      });
    }
  }, []);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        Загрузка…
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
          <Routes>
            <Route path="/" element={<ProductList />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/chat/:sessionId" element={<ChatWindow user={user} />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
