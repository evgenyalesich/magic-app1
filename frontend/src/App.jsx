import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import CatalogPage from './pages/CatalogPage';
import OrderConfirmation from './pages/OrderConfirmation';
import ChatPage from './pages/ChatPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/order/:orderId" element={<OrderConfirmation />} />
        <Route path="/chat/:orderId" element={<ChatPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
