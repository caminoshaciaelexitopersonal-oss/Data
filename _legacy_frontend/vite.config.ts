import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
        proxy: {
          // Proxy API requests to the backend during development
          '/unified': 'http://localhost:8000'
        }
      },
      plugins: [react()],
      // La clave de API ha sido eliminada del frontend por seguridad.
      // Debe ser gestionada a través de un endpoint proxy en el backend.
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
