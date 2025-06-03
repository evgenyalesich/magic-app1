import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css'; // обязательно подключи CSS Tailwind здесь!

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
