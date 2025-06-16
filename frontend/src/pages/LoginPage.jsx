// src/pages/LoginPage.jsx
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
    if (!raw) {
      setError("Нет initData от Telegram");
      return;
    }

    // 2) постим разобранный payload
    loginWithTelegram(raw)
      .then(() => {
        // 3) если login OK, сразу тащим профиль
        return qc.fetchQuery(["me"], fetchMe);
      })
      .then((me) => {
        if (!me) throw new Error("Не удалось получить профиль");
        navigate("/", { replace: true });
      })
      .catch((e) => {
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
