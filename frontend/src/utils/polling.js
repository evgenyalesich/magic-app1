import { apiClient } from "../api/client";
import toast from "react-hot-toast";

/**
 * Опрашивает сервер до тех пор, пока статус заказа не изменится на "paid".
 * @param {number} orderId - ID заказа для проверки.
 * @param {object} options - Настройки.
 * @param {number} options.interval - Интервал опроса в мс.
 * @param {number} options.timeout - Максимальное время ожидания в мс.
 * @returns {Promise<boolean>} - Возвращает true, если оплата прошла, иначе false.
 */
export function pollOrderStatus(
  orderId,
  { interval = 3000, timeout = 60000 } = {},
) {
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const checkStatus = async () => {
      // Проверяем таймаут
      if (Date.now() - startTime > timeout) {
        toast.error("Время ожидания оплаты истекло.");
        return resolve(false);
      }

      try {
        const { data } = await apiClient.get(`/payments/${orderId}/status`);

        if (data.status === "paid") {
          toast.success("Оплата подтверждена!");
          return resolve(true);
        }

        // Если статус всё ещё 'pending', продолжаем опрос
        setTimeout(checkStatus, interval);
      } catch (error) {
        console.error("Ошибка при проверке статуса заказа:", error);
        // В случае ошибки (например, 404), прекращаем опрос
        toast.error("Не удалось проверить статус оплаты.");
        return resolve(false);
      }
    };

    // Начинаем первую проверку
    checkStatus();
  });
}
