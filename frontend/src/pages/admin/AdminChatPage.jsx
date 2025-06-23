// src/pages/admin/AdminChatPage.jsx
import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import AdminChatWindow from "./AdminChatWindow";
import { fetchAdminMessages, sendAdminMessage } from "../../api/admin";

export default function AdminChatPage() {
  const { orderId } = useParams();
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetchAdminMessages(orderId).then(setMessages);
  }, [orderId]);

  async function handleSend(text) {
    const msg = await sendAdminMessage(orderId, text);
    setMessages((ms) => [...ms, msg]);
  }

  return (
    <div>
      <Link to="/admin/messages">← ко всем чатам</Link>
      <h2>Чат заказа #{orderId}</h2>
      <AdminChatWindow messages={messages} onSend={handleSend} />
    </div>
  );
}
