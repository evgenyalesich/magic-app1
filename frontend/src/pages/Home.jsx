import React, { useEffect, useState } from 'react';
import api from '../api';
import { setUserData } from '../utils/auth';
import { motion } from 'framer-motion';

const Home = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;

    if (tgUser) {
      const userData = {
        telegram_id: tgUser.id,
        username: tgUser.username || tgUser.first_name,
      };

      api.post('/api/auth/login', userData)
        .then(({ data }) => {
          setUserData(data);
          setUser(data);
        })
        .catch(err => console.error("Ошибка авторизации:", err));
    }
  }, []);

  return (
    <motion.div
      className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black text-white p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
          Magic App ✨
        </h1>
        {user ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <p className="text-xl md:text-2xl">Добро пожаловать, <span className="font-semibold">{user.username}</span>!</p>
            <p className="mt-2 text-purple-300">Рады видеть вас снова.</p>
          </motion.div>
        ) : (
          <p className="text-gray-400">Загрузка данных профиля...</p>
        )}
        <footer className="text-xs text-gray-600 absolute bottom-2 left-0 right-0">
          © 2025 Magic App. Все права защищены.
        </footer>
      </div>
    </motion.div>
  );
};

export default Home;
