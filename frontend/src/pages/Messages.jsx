import React, { useState, useEffect } from 'react';
import api from '../api';
import { getUserData } from '../utils/auth';

const Messages = () => {
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [message, setMessage] = useState('');
  const user = getUserData();

  useEffect(() => {
    if (user.is_admin) {
      api.get('/api/messages')
        .then(response => setChats(response.data))
        .catch(error => console.error('Ошибка загрузки чатов:', error));
    }
  }, [user]);

  const sendMessage = async () => {
    if (!message.trim() || !selectedChat) return;

    try {
      const response = await api.post('/api/messages/send', {
        chat_id: selectedChat.id,
        text: message
      });

      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === selectedChat.id
            ? { ...chat, messages: [...chat.messages, response.data] }
            : chat
        )
      );
      setMessage('');
    } catch (error) {
      console.error('Ошибка отправки сообщения:', error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">📨 Сообщения</h1>
      {user.is_admin ? (
        <div className="flex">
          <div className="w-1/3 bg-gray-800 p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3">💬 Чаты</h2>
            {chats.length > 0 ? (
              <ul>
                {chats.map(chat => (
                  <li
                    key={chat.id}
                    className={`p-2 cursor-pointer rounded-md ${selectedChat?.id === chat.id ? 'bg-gray-700' : 'hover:bg-gray-700'}`}
                    onClick={() => setSelectedChat(chat)}
                  >
                    {chat.username}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-400">Нет активных чатов</p>
            )}
          </div>

          <div className="w-2/3 bg-gray-900 p-4 rounded-lg ml-4">
            {selectedChat ? (
              <>
                <h2 className="text-xl font-semibold mb-3">
                  Чат с {selectedChat.username}
                </h2>
                <div className="h-64 overflow-y-auto p-3 bg-gray-800 rounded-lg">
                  {selectedChat.messages.map((msg, index) => (
                    <div
                      key={index}
                      className={`p-2 my-1 rounded-md ${msg.is_admin ? 'bg-purple-600 text-white' : 'bg-gray-700'}`}
                    >
                      {msg.text}
                    </div>
                  ))}
                </div>

                <div className="mt-4 flex">
                  <input
                    type="text"
                    className="flex-grow p-2 rounded-md bg-gray-700 border border-gray-600"
                    placeholder="Введите сообщение..."
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                  />
                  <button
                    onClick={sendMessage}
                    className="ml-2 px-4 py-2 bg-purple-600 text-white rounded-md"
                  >
                    Отправить
                  </button>
                </div>
              </>
            ) : (
              <p className="text-gray-400">Выберите чат для общения</p>
            )}
          </div>
        </div>
      ) : (
        <p className="text-gray-400">🔒 У вас нет доступа к сообщениям.</p>
      )}
    </div>
  );
};

export default Messages;
