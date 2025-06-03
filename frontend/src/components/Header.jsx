import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUserData } from '../utils/auth';
import api from '../api';

const Header = () => {
  const user = getUserData() || {}; // Защита от null
  const [unreadMessages, setUnreadMessages] = useState(0);

  useEffect(() => {
    if (user?.is_admin) {
      api.get('/api/messages/unread')
        .then(response => setUnreadMessages(response.data.count))
        .catch(error => console.error('Ошибка загрузки сообщений:', error));
    }
  }, [user]);

  return (
    <header className="bg-gray-900 text-white p-4 shadow-lg">
      <div className="container mx-auto flex justify-between items-center">
        {/* Логотип */}
        <h1 className="text-xl font-bold text-purple-400">Magic App</h1>

        <nav className="flex space-x-4">
          <Link to="/" className="hover:text-purple-400">Главная</Link>
          <Link to="/services" className="hover:text-purple-400">Услуги</Link>
          <Link to="/profile" className="hover:text-purple-400">Профиль</Link>
        </nav>

        {user?.is_admin && (
          <div className="relative group">
            <button className="hover:text-purple-400 font-bold">
              Админка ▼
            </button>
            <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <Link to="/admin/stats" className="block px-4 py-2 hover:bg-gray-700">Статистика</Link>
              <Link to="/admin/services" className="block px-4 py-2 hover:bg-gray-700">Услуги</Link>
              <Link to="/admin/messages" className="block px-4 py-2 hover:bg-gray-700">
                Сообщения {unreadMessages > 0 && (
                  <span className="bg-red-500 text-white px-2 py-1 rounded text-sm ml-1">
                    {unreadMessages}
                  </span>
                )}
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
