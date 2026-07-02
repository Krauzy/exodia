import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "Segoe UI", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "Cascadia Code", "Consolas", "ui-monospace", "SFMono-Regular"],
      },
      colors: {
        surface: {
          950: "#09090b",
          900: "#111113",
          800: "#1a1a1f",
          700: "#27272f",
        },
        accent: {
          cyan: "#22d3ee",
          green: "#22c55e",
          amber: "#f59e0b",
          red: "#ef4444",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
