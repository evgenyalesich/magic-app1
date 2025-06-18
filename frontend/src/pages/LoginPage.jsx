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
    console.group("🧪 [LoginPage] useEffect start");

    // 1) пытаемся взять initData
    let rawInit;
    if (window.Telegram?.WebApp?.initData) {
      rawInit = window.Telegram.WebApp.initData;
      console.log("  Got initData from Telegram.WebApp:", rawInit);
    } else {
      rawInit = searchParams.get("initData");
      console.log("  Got initData from URL:", rawInit);
    }
    console.log("  typeof rawInit:", typeof rawInit);

    if (!rawInit) {
      console.error("  No initData — abort");
      setError("Нет initData от Telegram");
      console.groupEnd();
      return;
    }

    // 2) логинимся на backend
    console.log("  Calling loginWithTelegram…");
    loginWithTelegram(rawInit)
      .then((loginData) => {
        console.log("  loginWithTelegram returned:", loginData);
        console.log("  Now fetching /auth/me…");
        // ===> ПРАВКА: передаём объект опций, а не два аргумента
        return qc.fetchQuery({
          queryKey: ["me"],
          queryFn: fetchMe,
        });
      })
      .then((me) => {
        console.log("  fetchMe returned:", me);
        if (!me) {
          throw new Error("Не удалось получить профиль пользователя");
        }
        console.log("  Navigation to '/'");
        navigate("/", { replace: true });
      })
      .catch((e) => {
        console.error("  ❌ [LoginPage] LoginPipe error:", e);
        const msg = e.response?.data?.message || e.message;
        setError(msg);
      })
      .finally(() => {
        console.groupEnd();
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
