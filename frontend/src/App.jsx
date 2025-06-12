
import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProductList from './components/ProductList';
import ProductDetail from './components/ProductDetail';
import ChatWindow from './components/ChatWindow';
import { telegramLogin, fetchCurrentUser } from './telegram';
import './App.css';

const queryClient = new QueryClient();

function InnerApp() {
  const navigate  = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        let profile = null;
        if (window.Telegram?.WebApp) {
          profile = await telegramLogin();
        } else {
          profile = await fetchCurrentUser();
        }

        if (profile) {
          setUser(profile);
          navigate('/', { replace: true });
        }
      } catch (err) {
        console.error('Auth error:', err);
      }
    })();
  }, [navigate]);

  if (!user) {
    return <div className="flex items-center justify-center h-screen">Загрузка…</div>;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path="/" element={<ProductList />} />
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route path="/chat/:sessionId" element={<ChatWindow user={user} />} />
      </Routes>
    </QueryClientProvider>
  );
}

export default function App() {
  return (
    <Router>
      <InnerApp />
    </Router>
  );
}
