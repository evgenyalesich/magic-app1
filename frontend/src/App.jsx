// File: frontend/src/App.jsx
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProductList from './components/ProductList';
import ProductDetail from './components/ProductDetail';
import ChatWindow from './components/ChatWindow';
import { initTelegram } from './telegram';
import './App.css';

const queryClient = new QueryClient();

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Пытаемся авторизоваться через Telegram WebApp
    initTelegram()
      .then(profile => {
        setUser(profile);
        // Устанавливаем тему телеграма
        const theme = window.Telegram.WebApp.colorScheme;
        document.documentElement.classList.toggle('dark', theme === 'dark');
      })
      .catch(err => {
        console.warn('Не удалось авторизоваться через Telegram:', err);
        // fallback: пробуем получить юзера по куки
        fetch(`${process.env.REACT_APP_API_BASE || ''}/api/auth/me`, {
          credentials: 'include'
        })
          .then(res => {
            if (!res.ok) throw new Error('No session');
            return res.json();
          })
          .then(setUser)
          .catch(() => {
            // оставляем user = null, покажем спиннер
          });
      });
  }, []);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        Загрузка...
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
