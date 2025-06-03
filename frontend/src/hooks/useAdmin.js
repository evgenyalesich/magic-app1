import { useState, useEffect } from 'react';

const ADMIN_TELEGRAM_ID = 1111111;

const useAdmin = (telegramId) => {
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    setIsAdmin(telegramId === ADMIN_TELEGRAM_ID);
  }, [telegramId]);

  return isAdmin;
};

export default useAdmin;
