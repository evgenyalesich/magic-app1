// src/pages/LoginPage.jsx

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { loginWithTelegram } from "../api/auth";

export default function LoginPage() {
  const [error, setError] = useState(null);
  const [searchParams] = useSearchParams();
  const nav = useNavigate();

  useEffect(() => {
    // 1) получаем payload
    // WebApp-версия
    const tgInitData = window.Telegram?.WebApp?.initData;
    // fallback — initData в URL, если открыли в браузере
    const urlInitData = searchParams.get("initData");

    const raw = tgInitData || urlInitData;
    let payload;
    try {
      if (!raw) throw new Error("No initData from Telegram");
      // Telegram передаёт initData строкой "k1=v1&k2=v2..."
      payload = Object.fromEntries(
        raw.split("&").map((pair) => {
          const [k, v] = pair.split("=");
          return [k, decodeURIComponent(v)];
        })
      );
    } catch (e) {
      setError(e.message);
      return;
    }

    // 2) POST на /auth/login
    loginWithTelegram(payload)
      .then(() => nav("/catalog"))
      .catch((e) => setError(e.message));
  }, [nav, searchParams]);

  return (
    <div className="h-screen flex items-center justify-center">
      {error ? (
        <div className="text-red-600">Ошибка входа: {error}</div>
      ) : (
        <div>Входим через Telegram…</div>
      )}
    </div>
  );
}
