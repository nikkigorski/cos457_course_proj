import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: process.cwd(),
  server: {
    port: 5173,
    host: 'localhost'
  }
})
