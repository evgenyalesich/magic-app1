// File: frontend/src/components/ProductDetail.jsx
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchProduct, createOrder } from '../services/api';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: product, isLoading, error } = useQuery(['product', id], () => fetchProduct(id));
  const tg = window.Telegram.WebApp;

  useEffect(() => {
    if (product) {
      tg.MainButton.text = `Купить за ${product.price} ₽`;
      tg.MainButton.show();
      tg.onEvent('mainButtonClicked', handleBuy);
      document.documentElement.classList.toggle('dark', tg.colorScheme === 'dark');
      tg.expand();
    }
    return () => {
      tg.MainButton.hide();
      tg.offEvent('mainButtonClicked', handleBuy);
    };
  }, [product]);

  async function handleBuy() {
    try {
      const { chatSessionId } = await createOrder(id);
      navigate(`/chat/${chatSessionId}`);
    } catch (err) {
      console.error(err);
      alert('Ошибка при оформлении заказа');
    }
  }

  if (isLoading) return <div className="p-4">Загрузка...</div>;
  if (error) return <div className="p-4 text-red-500">Ошибка: {error.message}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">{product.name}</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <img
          src={product.imageUrl}
          alt={product.name}
          className="w-full h-64 object-cover rounded-lg"
        />
        <div>
          <p className="mb-4">{product.description}</p>
          <p className="font-bold text-xl mb-4">{product.price} ₽</p>
        </div>
      </div>
    </div>
  );
}
