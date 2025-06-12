import { useEffect, useState } from 'react'
import { fetchProducts, createOrder } from '../api/products'

export default function CatalogPage() {
  const [items, setItems] = useState([])

  useEffect(() => {
    fetchProducts().then(setItems)
  }, [])

  return (
    <div className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map(item => (
        <div key={item.id} className="border rounded-lg p-4 shadow">
          <img src={item.image_url} alt={item.title} className="w-full h-48 object-cover mb-2"/>
          <h2 className="text-xl font-semibold">{item.title}</h2>
          <p className="text-gray-600">{item.description}</p>
          <div className="mt-4 flex justify-between items-center">
            <span className="font-bold">{item.price} ₽</span>
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded"
              onClick={() => createOrder(item.id).then(() => alert('Заказ оформлен'))}
            >
              Купить
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
