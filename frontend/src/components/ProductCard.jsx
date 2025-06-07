// File: frontend/src/components/ProductCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function ProductCard({ product }) {
  const navigate = useNavigate();

  return (
    <div
      className="border rounded-lg overflow-hidden shadow hover:shadow-lg transition cursor-pointer bg-white dark:bg-gray-800"
      onClick={() => navigate(`/product/${product.id}`)}
    >
      <img
        src={product.imageUrl}
        alt={product.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-2">{product.name}</h2>
        <p className="font-bold mb-2">{product.price} ₽</p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {product.shortDescription}
        </p>
      </div>
    </div>
  );
}
