// src/api/auth.js
const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

export async function loginWithTelegram(payload) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Login failed: ${text}`);
  }
  return res.json();
}



