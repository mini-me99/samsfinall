import { defineBoot } from '#q-app/wrappers';
import axios, { type AxiosInstance } from 'axios';

declare module 'vue' {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string) || '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sams_access');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default defineBoot(({ app }) => {
  app.config.globalProperties.$api = api;
});

export { api };
