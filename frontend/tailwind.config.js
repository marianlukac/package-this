/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        dm: {
          blue: '#1e3a5f',
          gold: '#c9a227',
          paper: '#f5f0e8',
          ink: '#1a1a2e',
        }
      }
    },
  },
  plugins: [],
}
