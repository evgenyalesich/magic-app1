import axios from "axios";

// Меняем базовый URL сразу на /api, чтобы в компонентах дальше не дублировать этот префикс
const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
