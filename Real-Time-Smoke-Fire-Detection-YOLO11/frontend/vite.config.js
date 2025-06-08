import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/run-yolo': 'http://localhost:5000',
      '/stop-yolo': 'http://localhost:5000'
    }
  }
})
