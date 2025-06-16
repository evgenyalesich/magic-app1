// src/api/index.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "", // или просто '/api'
  withCredentials: true, // важно, чтобы куки шли автоматически
});

export default api;
