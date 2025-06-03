import React, { useState, useEffect } from 'react';
import api from '../api';
import { motion } from 'framer-motion';

const Services = () => {
  const [services, setServices] = useState([]);

  useEffect(() => {
    api.get('/products')
      .then((response) => {
        setServices(response.data);
      })
      .catch((error) => console.error("Ошибка получения услуг:", error));
  }, []);

  return (
    <motion.div
      className="p-6 container mx-auto"
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <h1 className="text-3xl font-bold mb-4">Наши услуги</h1>
      {services.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map(service => (
            <div key={service.id} className="border p-4 rounded shadow hover:shadow-xl transition-shadow">
              <h2 className="text-xl font-semibold">{service.title}</h2>
              <p className="mt-2">{service.description}</p>
              <p className="mt-4 font-bold">${service.price}</p>
            </div>
          ))}
        </div>
      ) : (
        <p>Загрузка услуг...</p>
      )}
    </motion.div>
  );
};

export default Services;
