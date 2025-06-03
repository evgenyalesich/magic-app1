import React, { useState, useEffect } from 'react';
import api from '../api';

const AdminServiceForm = () => {
  const [services, setServices] = useState([]);
  const [newService, setNewService] = useState({ title: '', description: '', image_url: '', price: '' });

  useEffect(() => {
    api.get('/api/services').then(res => setServices(res.data));
  }, []);

  const createService = () => {
    api.post('/api/services', newService).then(({data}) => {
      setServices([...services, data]);
      setNewService({ title: '', description: '', image_url: '', price: '' });
    });
  };

  return (
    <div className="mb-10">
      <input className="input" placeholder="Название" value={newService.title} onChange={e => setNewService({...newService, title: e.target.value})} />
      <input className="input" placeholder="Описание" value={newService.description} onChange={e => setNewService({...newService, description: e.target.value})} />
      <input className="input" placeholder="URL картинки" value={newService.image_url} onChange={e => setNewService({...newService, image_url: e.target.value})} />
      <input className="input" placeholder="Цена" value={newService.price} type="number" onChange={e => setNewService({...newService, price: e.target.value})} />
      <button className="btn bg-purple-500 mt-3" onClick={createService}>Добавить услугу</button>
    </div>
  );
};

export default AdminServiceForm;
