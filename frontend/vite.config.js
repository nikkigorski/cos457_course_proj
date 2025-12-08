import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  root: process.cwd(),
  server: {
    port: 5173,
    host: "localhost"
  },

  // load account creation
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        professor: resolve(__dirname, "professor.html"),
        student: resolve(__dirname, "student.html"),
      },
    },
  },
  resolve: {
    extensions: [".js", ".jsx", ".ts", ".tsx"],
  }
});
