/** @type {import('tailwindcss').Config} */
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#1a1b26",
        "bg-dark": "#13141c",
        panel: "#16161e",
        input: "#1f2335",
        border: "#292e42",
        "border-lit": "#3b4261",
        fg: "#c0caf5",
        "fg-dim": "#565f89",
        "fg-dimmer": "#414868",
        blue: "#7aa2f7",
        purple: "#bb9af7",
        cyan: "#7dcfff",
        green: "#9ece6a",
        yellow: "#e0af68",
        orange: "#ff9e64",
        red: "#f7768e",
      },
      fontFamily: {
        mono: ["'Fira Code'", "'FiraCode Nerd Font'", "ui-monospace", "'JetBrains Mono'", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};
