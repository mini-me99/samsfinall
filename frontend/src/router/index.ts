import { defineRouter } from '#q-app/wrappers';
import { createRouter, createMemoryHistory, createWebHistory } from 'vue-router';
import routes from './routes';

export default defineRouter(() => {
  const createHistory = process.env.SERVER ? createMemoryHistory : createWebHistory;
  return createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });
});
