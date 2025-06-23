// src/api/profile.js
const API_BASE = import.meta.env.VITE_API_URL || "";

export async function getProfile() {
  const res = await fetch(`${API_BASE}/api/profile`, {
    credentials: "include",
  });
  if (!res.ok) throw new Error("Не удалось получить профиль");
  return res.json(); // { id, name, stars, ... }
}
