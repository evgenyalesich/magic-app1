// File: frontend/src/components/ChatWindow.jsx
import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { fetchChatHistory, sendMessage } from '../services/api';

export default function ChatWindow({ user }) {
  const { sessionId } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const wsRef = useRef(null);

  useEffect(() => {
    async function loadHistory() {
      const history = await fetchChatHistory(sessionId);
      setMessages(history);
    }
    loadHistory();

    const ws = new WebSocket(`wss://your-domain.com/chat/${sessionId}`);
    ws.onmessage = e => {
      const msg = JSON.parse(e.data);
      setMessages(prev => [...prev, msg]);
    };
    wsRef.current = ws;

    return () => ws.close();
  }, [sessionId]);

  const handleSend = async () => {
    const msg = { text: input, sender: user.name };
    wsRef.current.send(JSON.stringify(msg));
    setMessages(prev => [...prev, msg]);
    setInput('');
    await sendMessage(sessionId, msg);
  };

  return (
    <div className="flex flex-col h-screen p-4">
      <div className="flex-1 overflow-auto mb-4">
        {messages.map((m, idx) => (
          <div key={idx} className={m.sender === user.name ? 'text-right' : 'text-left'}>
            <span className="inline-block px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded-lg mb-1">
              <strong>{m.sender}:</strong> {m.text}
            </span>
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          className="flex-1 border rounded-l-lg p-2"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Введите сообщение"
        />
        <button
          className="bg-blue-500 text-white px-4 rounded-r-lg"
          onClick={handleSend}
        >
          Отправить
        </button>
      </div>
    </div>
  );
}
