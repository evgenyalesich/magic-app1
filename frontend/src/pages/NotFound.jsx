import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="p-6 container mx-auto text-center">
      <h1 className="text-4xl font-bold mb-4">404 - Страница не найдена</h1>
      <p className="mb-4">Извините, страница, которую вы ищете, не существует.</p>
      <Link to="/" className="text-blue-500 hover:underline">
        Вернуться на главную
      </Link>
    </div>
  );
};

export default NotFound;
