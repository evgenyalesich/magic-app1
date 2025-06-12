// File: frontend/src/components/ProductList.jsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchProducts } from '../services/api';
import ProductCard from './ProductCard';

export default function ProductList() {
  const { data: products, isLoading, error } = useQuery(['products'], fetchProducts);

  if (isLoading) {
    return <div className="p-4">Загрузка товаров...</div>;
  }
  if (error) {
    return <div className="p-4 text-red-500">Ошибка: {error.message}</div>;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 p-4">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
