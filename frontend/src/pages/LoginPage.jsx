import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { loginWithTelegram } from "../api/auth";
import styles from "./LoginPage.module.css";

const log = (...args) => console.log("[LoginPage]", ...args);
const logError = (...args) => console.error("[LoginPage]", ...args);

export default function LoginPage() {
  const [error, setError] = useState(null);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  useEffect(() => {
    log("🚀 Компонент смонтирован, запускается useEffect для входа.");

    qc.clear();
    log("✅ Кэш React Query очищен.");

    console.group("🧪 [LoginPage] Процесс входа запущен");

    let rawInit;
    if (window.Telegram?.WebApp?.initData) {
      rawInit = window.Telegram.WebApp.initData;
    } else {
      rawInit = searchParams.get("initData");
    }

    if (!rawInit) {
      setError("Нет данных для входа от Telegram (initData).");
      console.groupEnd();
      return;
    }

    log("Шаг 1: Успешно получены initData.");
    log("Шаг 2: Вызов `loginWithTelegram`...");

    loginWithTelegram(rawInit)
      .then((user) => {
        // Переменная теперь называется user для ясности
        log("Шаг 3: Получен объект пользователя от auth.js.");
        console.log("  ✅ Объект пользователя:", user);

        // --- ЭТО КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ---
        // Проверяем, что 'user' это действительно объект и у него есть id
        if (!user || typeof user !== "object" || !user.id) {
          logError(
            "  ❌ ОШИБКА: Полученные данные не являются валидным объектом пользователя.",
          );
          throw new Error("Ответ от сервера не содержит данных пользователя.");
        }

        log("  📋 Данные пользователя:", user);

        log("Шаг 4: Помещение данных пользователя в кэш React Query...");
        qc.setQueryData(["me"], user);
        log("  ✅ Данные пользователя успешно помещены в кэш.");

        log("Шаг 5: Навигация на главную страницу '/'...");
        navigate("/", { replace: true });
      })
      .catch((e) => {
        logError("  ❌ [LoginPage] Ошибка в процессе входа:", e);
        const msg =
          e.response?.data?.detail || e.response?.data?.message || e.message;
        setError(msg);
      })
      .finally(() => {
        log("🏁 Процесс входа завершен.");
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
