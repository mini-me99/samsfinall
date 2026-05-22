import { defineConfig } from '#q-app/wrappers';

export default defineConfig((/* ctx */) => ({
  // ORDER MATTERS: pinia must come before auth (auth uses a store).
  boot: ['i18n', 'pinia', 'axios', 'auth'],
  css: ['app.scss'],
  extras: ['roboto-font', 'material-icons'],
  build: {
    target: { browser: ['es2022'], node: 'node20' },
    vueRouterMode: 'history',
    typescript: { strict: true, vueShim: true },
    env: {
      API_URL: process.env.VITE_API_URL || 'http://localhost/api',
    },
  },
  devServer: {
    open: false,
    host: '0.0.0.0',
    port: 9000,
  },
  framework: {
    config: {},
    plugins: ['Notify', 'Dialog', 'Loading'],
    lang: 'en-US',
  },
  animations: [],
  ssr: { prodPort: 3000, middlewares: ['render'], pwa: false },
}));
