// src/hooks/useCurrentUser.js
import { useState, useEffect } from "react";
import { apiClient } from "../api/client";

export function useCurrentUser() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    apiClient
      .get("/auth/me")
      .then(({ data }) => setUser(data))
      .catch(() => setUser(null));
  }, []);
  return user;
}
