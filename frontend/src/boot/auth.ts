import { defineBoot } from '#q-app/wrappers';
import { useAuthStore } from 'src/stores/auth';

// Pinia is registered by boot/pinia.ts (which must run BEFORE this file).
export default defineBoot(({ router }) => {
  const auth = useAuthStore();
  auth.loadFromStorage();
  router.beforeEach(async (to) => {
    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { path: '/login', query: { redirect: to.fullPath } };
    }
    if (to.meta.requiresAuth && auth.isAuthenticated && !auth.user) {
      try { await auth.fetchMe(); } catch { /* noop */ }
    }
    const roles = to.meta.roles as string[] | undefined;
    if (roles && auth.user && !roles.includes(auth.user.role)) {
      return { path: '/' };
    }
  });
});
