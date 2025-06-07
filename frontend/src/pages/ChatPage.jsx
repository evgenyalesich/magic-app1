// frontend/src/pages/ChatPage.jsx
import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { fetchMessages, sendMessage } from '../api/chat';

export default function ChatPage() {
  const { orderId } = useParams();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const bottomRef = useRef();

  useEffect(() => {
    // подгружаем историю чата
    fetchMessages(orderId).then(setMessages);
  }, [orderId]);

  useEffect(() => {
    // скроллим вниз при обновлении
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!text.trim()) return;
    const msg = await sendMessage(orderId, text);
    setMessages((prev) => [...prev, msg]);
    setText('');
  };

  return (
    <div className="chat-page">
      <h1>Чат по заказу #{orderId}</h1>
      <div className="messages-list" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.is_admin ? 'admin' : 'user'}`}>
            <div className="text">{m.content}</div>
            <div className="time">{new Date(m.created_at).toLocaleTimeString()}</div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="input-area">
        <input
          type="text"
          placeholder="Ваше сообщение..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Отправить</button>
      </div>
    </div>
  );
}
