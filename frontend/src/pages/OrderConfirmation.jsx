
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchOrder } from '../api/orders';

export default function OrderConfirmation() {
  const { orderId } = useParams();
  const nav = useNavigate();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOrder(orderId)
      .then(setOrder)
      .catch(err => setError(err.message));
  }, [orderId]);

  if (error) return <p className="text-red-500">Ошибка: {error}</p>;
  if (!order) return <p>Загрузка...</p>;

  const { product, status, created_at } = order;

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Заказ №{order.id}</h1>
      <p><strong>Услуга:</strong> {product.name}</p>
      <p><strong>Описание:</strong> {product.description}</p>
      <p><strong>Цена:</strong> {product.price} ₽</p>
      <p><strong>Дата:</strong> {new Date(created_at).toLocaleString()}</p>
      <p><strong>Статус:</strong> {status}</p>
      <button
        onClick={() => nav(`/chat/${order.id}`)}
        className="mt-6 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Написать в чат
      </button>
    </div>
  );
}
