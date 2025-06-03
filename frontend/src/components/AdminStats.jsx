import React, { useEffect, useState } from 'react';
import api from '../api';

const AdminStats = () => {
  const [stats, setStats] = useState({});

  useEffect(() => {
    api.get('/api/admin/stats').then(res => setStats(res.data));
  }, []);

  return (
    <div className="grid grid-cols-3 gap-4 text-white mb-10">
      <div className="bg-gray-800 p-4 rounded-xl">Пользователей: {stats.total_users}</div>
      <div className="bg-gray-800 p-4 rounded-xl">Заказов: {stats.total_orders}</div>
      <div className="bg-gray-800 p-4 rounded-xl">Сумма заказов: {stats.total_income} ₽</div>
    </div>
  );
};

export default AdminStats;
