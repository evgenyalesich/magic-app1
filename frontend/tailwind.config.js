// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#6d5dfc",
          500: "#6d5dfc",
          400: "#7e6bff",
          300: "#8f7aff",
        },
        beige: "#f5f0e8",
      },
      boxShadow: { soft: "0 4px 16px rgba(0, 0, 0, .08)" },
    },
  },
  plugins: [],
};
