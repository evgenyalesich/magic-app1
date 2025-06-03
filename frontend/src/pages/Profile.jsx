import React from 'react';
import { Link } from 'react-router-dom';
import { getUserData } from '../utils/auth';
import { motion } from 'framer-motion';

const Profile = () => {
  // Забираем из localStorage то, что записали при логине
  const user = getUserData();

  if (!user) {
    return <div className="text-center text-red-500">Нет данных о пользователе.</div>;
  }

  return (
    <motion.div
      className="container mx-auto p-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <h2 className="text-2xl font-semibold mb-4">Профиль: {user.username}</h2>
      <p className="mb-2">Telegram ID: {user.telegram_id}</p>

      {user.is_admin && (
        <Link
          to="/admin"
          className="inline-block mt-4 px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition"
        >
          Перейти в админ‑панель
        </Link>
      )}
    </motion.div>
  );
};

export default Profile;
