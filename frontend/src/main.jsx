// frontend/src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { Toaster } from "react-hot-toast";
import "./index.css";
// 1) Сначала Tailwind
import "./assets/tailwind.css";

import App from "./App.jsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={new QueryClient()}>
      <Toaster position="top-center" />
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
