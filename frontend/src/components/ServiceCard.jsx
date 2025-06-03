import React from 'react';

const ServiceCard = ({ service }) => (
  <div className="max-w-sm rounded-2xl shadow-lg bg-gray-900 text-white">
    <img className="w-full h-48 object-cover" src={service.image_url} alt={service.title} />
    <div className="px-6 py-4">
      <div className="font-bold text-xl">{service.title}</div>
      <p className="text-gray-300 text-base">{service.description}</p>
      <p className="text-purple-400 font-semibold text-lg mt-2">{service.price}₽</p>
      <button className="mt-3 w-full bg-purple-500 py-2 rounded-lg hover:bg-purple-700 transition">
        Заказать
      </button>
    </div>
  </div>
);

export default ServiceCard;
