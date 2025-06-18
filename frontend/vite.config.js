// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    react({
      // этот параметр по умолчанию — "automatic",
      // но если у тебя стоял "classic", поменяй на "automatic"
      jsxRuntime: "automatic",
    }),
  ],
});
