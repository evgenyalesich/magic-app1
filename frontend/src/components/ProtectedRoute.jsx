import React from 'react';
import { Navigate } from 'react-router-dom';
import { getUserData } from '../utils/auth';

const ProtectedRoute = ({ children }) => {
  const user = getUserData();
  return user && user.is_admin ? children : <Navigate to="/" replace />;
};

export default ProtectedRoute;
