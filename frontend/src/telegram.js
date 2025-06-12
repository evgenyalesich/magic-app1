
const API_BASE = import.meta.env.VITE_API_BASE;
if (!API_BASE) {
  throw new Error('VITE_API_BASE не задан в .env');
}

/**
 *  Telegram Web-View login chain
 *
 *   1) POST /api/auth/login   – отправляем initDataUnsafe (JSON),
 *                               сервер ставит куку  tg_id
 *   2) GET  /api/auth/me      – читаем профиль по этой куке
 */
export async function telegramLogin() {
  console.log('[tg-login] ⚡ start');

  const tg = window.Telegram?.WebApp;
  if (!tg) throw new Error('[tg-login] Telegram.WebApp is undefined');

  tg.ready();
  tg.expand();

  /* ---------- raw payload from Telegram ---------- */
  const initData = tg.initDataUnsafe;          // объект!
  console.log('[tg-login] initDataUnsafe =', initData);

  if (!initData?.hash) {
    throw new Error('[tg-login] initData.hash is empty – Web-View запущен не по кнопке «Open Web-App»');
  }

  /* ---------- 1.  POST /login ---------- */
  console.log('[tg-login] POST /login …');
  const loginRes = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(initData),
  });

  if (!loginRes.ok) {
    const txt = await loginRes.text();
    console.error('[tg-login] ❌ /login failed', loginRes.status, txt);
    throw new Error(`login ${loginRes.status}: ${txt}`);
  }
  console.log('[tg-login] ✅ /login 200 OK → cookie set?');

  /* ---------- 2.  GET /me ---------- */
  console.log('[tg-login] GET  /me …');
  const meRes = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: 'include',
  });

  if (!meRes.ok) {
    const txt = await meRes.text();
    console.error('[tg-login] ❌ /me failed', meRes.status, txt);
    throw new Error(`/me ${meRes.status}: ${txt}`);
  }

  const profile = await meRes.json();
  console.log('[tg-login] 🎉 success → profile =', profile);
  return profile;
}

/* ---------- fallback: обычный браузер с уже поставленной кукой ---------- */
export async function fetchCurrentUser() {
  console.log('[tg-login] fetchCurrentUser');
  const res = await fetch(`${API_BASE}/api/auth/me`, { credentials: 'include' });
  return res.ok ? res.json() : null;
}
