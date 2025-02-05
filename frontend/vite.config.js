import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server:{
    port:3000,  //Redirect the frontend to the port 3000 if not the default one 
    proxy:{
      'api':{
        target:'http://127.0.0.1:5000', //Redirect API calls to flask,
        changeOrigin: true,
        secure: false, //Disable SSL verification or not
      }
    }
  }
})
