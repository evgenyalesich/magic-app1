import React, { useState, useEffect } from 'react';
import AdminServiceForm from '../components/AdminServiceForm';
import AdminStats from '../components/AdminStats';
import Chat from '../components/Chat';
import { getUserData } from '../utils/auth';
import api from '../api';

const Admin = () => {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const userData = getUserData();
    setUser(userData);

    if (userData?.telegram_id) {
      api.get(`/api/admin/dashboard?telegram_id=${userData.telegram_id}`)
        .then(res => setStats(res.data))
        .catch(err => console.error('Ошибка запроса статистики', err));
    }
  }, []);

  if (!user) {
    return <p className="text-center text-gray-400">🔄 Загрузка...</p>;
  }

  if (!user.is_admin) {
    return <h1 className="text-center text-red-500 mt-10">🚫 Доступ запрещен</h1>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-purple-500">Админ-панель 🛠️</h1>
      {stats && <AdminStats data={stats} />}
      <AdminServiceForm />
      <Chat />
    </div>
  );
};

export default Admin;
