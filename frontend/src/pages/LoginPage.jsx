import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { loginWithTelegram, fetchMe } from "../api/auth";
import styles from "./LoginPage.module.css";

export default function LoginPage() {
  const [error, setError] = useState(null);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  useEffect(() => {
    // 1) берём initData из WebApp или URL
    const raw =
      window.Telegram?.WebApp?.initData || searchParams.get("initData");

    console.log("🧪 [LoginPage] raw initData =", raw); // 👈 DEBUG

    if (!raw) {
      setError("Нет initData от Telegram");
      return;
    }

    // 2) логинимся на backend
    loginWithTelegram(raw)
      .then(() => {
        console.log("✅ [LoginPage] Login successful"); // 👈 DEBUG

        // 3) тащим профиль юзера
        return qc.fetchQuery(["me"], fetchMe);
      })
      .then((me) => {
        if (!me) throw new Error("Не удалось получить профиль");
        console.log("👤 [LoginPage] User profile:", me); // 👈 DEBUG

        navigate("/", { replace: true });
      })
      .catch((e) => {
        console.error("❌ [LoginPage] Ошибка логина:", e); // 👈 DEBUG
        setError(e.response?.data?.message || e.message);
      });
  }, [qc, navigate, searchParams]);

  return (
    <div className={styles.page}>
      {error ? (
        <div className={styles.error}>Ошибка входа: {error}</div>
      ) : (
        <div className={styles.loading}>Входим через Telegram…</div>
      )}
    </div>
  );
}
