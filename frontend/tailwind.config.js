/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        maroon: {
          50: '#fdf2f4',
          100: '#fbe6e9',
          200: '#f7ccd3',
          300: '#f0a3b0',
          400: '#e56f85',
          500: '#d44362',
          600: '#b92849',
          700: '#9b1c3a',
          800: '#881337',
          900: '#800020',
          950: '#460816',
        },
        apex: {
          bgWhite: '#ffffff',
          bgOffWhite: '#f8fafc',
          bgSurface: '#ffffff',
          maroonBorder: 'rgba(128, 0, 32, 0.20)',
          maroonBorderHover: 'rgba(128, 0, 32, 0.40)',
          primary: '#800020',
          primaryHover: '#68001a',
          accent: '#9b1c3a',
          accentHover: '#881337',
          textDark: '#0f172a',
          textMuted: '#475569',
          borderLight: 'rgba(128, 0, 32, 0.15)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Outfit', 'sans-serif'],
      },
      boxShadow: {
        'maroon': '0 4px 20px -2px rgba(128, 0, 32, 0.12)',
        'maroon-lg': '0 10px 30px -4px rgba(128, 0, 32, 0.18)',
      }
    },
  },
  plugins: [],
}
