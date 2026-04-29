import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Necesario para acceder desde Docker
    port: 5173,
    watch: {
      usePolling: true, // Útil para Docker en Windows (WSL2/Hyper-V)
    }
  }
})
