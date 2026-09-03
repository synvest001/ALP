import { defineConfig } from 'vite';
import legacy from '@vitejs/plugin-legacy';

export default defineConfig({
  base: './', // Ensure relative paths for GH Pages and Offline PWA
  plugins: [
    legacy({
      targets: ['> 0.2%', 'not dead', 'iOS >= 9'],
      additionalLegacyPolyfills: ['regenerator-runtime/runtime'],
      renderLegacyChunks: true,
      polyfills: true,
    })
  ],
  build: {
    target: 'es2015',
    cssTarget: 'chrome61', 
    outDir: 'dist',
    emptyOutDir: true
  }
});
