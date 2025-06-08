// File: frontend/src/App.jsx
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProductList from './components/ProductList';
import ProductDetail from './components/ProductDetail';
import ChatWindow from './components/ChatWindow';
import './App.css';

const API_BASE = process.env.REACT_APP_API_BASE;

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      const payload = tg.initDataUnsafe;

      // 👉 вот сюда вставляем логин
      fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(res => {
          if (!res.ok) throw new Error('Login failed');
          return res.json();
        })
        .then(() => {
          // 👉 и сразу запросим /me
          return fetch(`${API_BASE}/api/auth/me`, { credentials: 'include' });
        })
        .then(res => {
          if (!res.ok) throw new Error('Не авторизован');
          return res.json();
        })
        .then(profile => setUser(profile))
        .catch(console.error);

      const theme = tg.colorScheme;
      document.documentElement.classList.toggle('dark', theme === 'dark');
    } else {
      fetch(`${API_BASE}/api/auth/me`, { credentials: 'include' })
        .then(res => res.json())
        .then(setUser)
        .catch(() => {});
    }
  }, []);

  if (!user) {
    return <div className="flex items-center justify-center h-screen">Загрузка...</div>;
  }

  return (
    <QueryClientProvider client={new QueryClient()}>
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
