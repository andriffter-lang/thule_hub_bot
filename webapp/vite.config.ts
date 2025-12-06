import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/https://github.com/andriffter-lang/thule_hub_bot.git/",
  build: {
    outDir: "../docs",     // собирать сразу в /docs в корне репо
    emptyOutDir: true,     // очищать /docs перед сборкой
  },
});
