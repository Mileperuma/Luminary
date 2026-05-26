/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Calm, light palette — see Doc 2 Section 9.1
      colors: {
        cream: "#FAF8F5",       // background
        ink: "#2A2A2A",         // primary text
        muted: "#6B6B6B",       // secondary text
        accent: "#7E9CB0",      // single accent — soft blue, active states only
        card: "#FFFFFF",
        line: "#E8E4DE",        // hairline dividers
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["Fraunces", "Georgia", "serif"],
      },
      borderRadius: {
        lg: "0.625rem",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04)",
      },
    },
  },
  plugins: [],
};
