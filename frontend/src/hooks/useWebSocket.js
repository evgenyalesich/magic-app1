// src/hooks/useWebSocket.js
import { useEffect, useRef, useCallback, useState } from "react";

export default function useWebSocket(chatId, userId, onMessage) {
  const socketRef = useRef(null);
  const reconnectRef = useRef(null);
  const mountedRef = useRef(false);
  const [isConnected, setIsConnected] = useState(false);

  // Храним onMessage в ref, чтобы не вызывать эффект reconnect при каждом render
  const onMessageRef = useRef(onMessage);
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    if (!chatId || !userId || !mountedRef.current) return;

    // Если было старое соединение — аккуратно закрываем
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }

    const ws = new WebSocket(
      `wss://zerkalo-sudby.ru/api/ws/messages/${chatId}?user_id=${userId}`,
    );

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (evt) => {
      try {
        onMessageRef.current(JSON.parse(evt.data));
      } catch (err) {
        console.error("WS parse error:", err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      socketRef.current = null;
      // Переподключаемся только если компонент ещё «жив»
      if (mountedRef.current) {
        reconnectRef.current = setTimeout(() => {
          connect();
        }, 3000);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    socketRef.current = ws;
  }, [chatId, userId]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      // флаг, что уже размонтированы
      mountedRef.current = false;
      // чистим потенциальный таймаут переподключения
      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current);
      }
      // закрываем WS
      socketRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((msg) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return { sendMessage, isConnected };
}
