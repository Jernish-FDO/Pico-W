// tailwind.config.js

/** @type {import('tailwindcss').Config} */
// Change this line:
// export default {

// To this:
module.exports = {
  content: [
    "./index.html",
    "./js/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}