// src/pages/admin/AdminReportPage.jsx
import React, { useEffect, useState } from "react";
import styles from "./AdminReportPage.module.css";
import { fetchAdminReport } from "../../api/admin";

export default function AdminReportPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadReport();
  }, []);

  async function loadReport() {
    setLoading(true);
    setError("");
    try {
      const data = await fetchAdminReport();
      setReport(data);
    } catch (err) {
      console.error(err);
      setError("Не удалось загрузить отчёт");
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className={styles.placeholder}>Загрузка…</div>;
  if (error) return <div className={styles.placeholder}>{error}</div>;

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Отчёт / Статистика</h2>
      <div className={styles.grid}>
        {Object.entries(report).map(([key, value]) => (
          <div key={key} className={styles.card}>
            <div className={styles.value}>{value}</div>
            <div className={styles.label}>
              {key
                .replace(/([A-Z])/g, " $1")
                .replace(/^./, (str) => str.toUpperCase())}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
