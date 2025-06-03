import axios from 'axios';

const api = axios.create({
  baseURL: 'https://jacket-days-easter-bald.trycloudflare.com/api', // адрес бекенда
});

export default api;
