/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#05060B",      // base background — deep space, blue-black
        abyss: "#0A0E1A",     // recessed panel background
        panel: "#0D1120",     // console panel background
        ink: "#EDEFF7",       // primary text
        mist: "#8791A8",      // secondary / muted text
        electric: "#4DA3FF",  // electric blue — primary actions, links
        verdant: "#22E6A8",   // emerald — true / high trust
        violet: "#B678FF",    // neon purple — misleading / radar accent
        rose: "#FF4D6D",      // false / low trust
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        sans: ["'Inter'", "sans-serif"],
        bn: ["'Noto Sans Bengali'", "sans-serif"],
      },
      keyframes: {
        "ring-in": {
          "0%": { opacity: 0, transform: "scale(0.96) translateY(6px)" },
          "100%": { opacity: 1, transform: "scale(1) translateY(0)" },
        },
        marquee: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        "pulse-dot": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.35 },
        },
      },
      animation: {
        "card-in": "ring-in 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        marquee: "marquee 28s linear infinite",
        "pulse-dot": "pulse-dot 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};