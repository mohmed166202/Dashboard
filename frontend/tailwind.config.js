/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        header: {
          bg: "var(--header-bg)",
          text: "var(--header-text)",
        },
        row: {
          odd: "var(--row-odd)",
          even: "var(--row-even)",
        },
        highlight: "var(--highlight)",
        border: "var(--border)",
        textMain: "var(--text)",
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
      },
      boxShadow: {
        'subtle': '0 2px 8px -2px rgba(74, 52, 38, 0.08), 0 1px 3px -1px rgba(74, 52, 38, 0.06)',
        'card': '0 4px 16px -4px rgba(74, 52, 38, 0.12), 0 2px 6px -2px rgba(74, 52, 38, 0.08)',
      }
    },
  },
  plugins: [],
}
