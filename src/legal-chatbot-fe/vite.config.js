import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // server: {
  // //  proxy: {
  // //   '/api': {
  // //     target: 'http://localhost:8000', // backend local
  // //     changeOrigin: true,
  // //     secure: false
  // //   }
  // // },
  //  allowedHosts: [
  //     'nutten-gnu-termination-jennifer.trycloudflare.com',
  //     'localhost',
  //   ],
  // host: true,
  // port: 5173
  // },
})