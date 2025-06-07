// src/components/ProductCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { createOrder } from '../api/orders';

export default function ProductCard({ product }) {
  const nav = useNavigate();

  const handleBuy = async () => {
    try {
      const order = await createOrder(product.id);
      nav(`/order/${order.id}`);
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div className="border rounded p-4 shadow-sm">
      <img src={product.image_url} alt={product.name} className="w-full h-48 object-cover mb-2" />
      <h2 className="text-xl font-semibold mb-1">{product.name}</h2>
      <p className="text-gray-600 mb-2">{product.description}</p>
      <p className="font-bold mb-4">{product.price} ₽</p>
      <button
        onClick={handleBuy}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Купить
      </button>
    </div>
  );
}
