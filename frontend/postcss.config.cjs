// frontend/postcss.config.cjs
/* eslint-env node */
module.exports = {
  plugins: {
    // вот здесь используем именно @tailwindcss/postcss
    "@tailwindcss/postcss": {},
    autoprefixer: {},
  },
};
