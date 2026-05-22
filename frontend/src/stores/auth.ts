import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';

interface User {
  id: string;
  email: string;
  role: string;
  academy: string | null;
  first_name?: string;
  last_name?: string;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: null as string | null,
    refresh: null as string | null,
    user: null as User | null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.access,
  },
  actions: {
    loadFromStorage() {
      this.access = localStorage.getItem('sams_access');
      this.refresh = localStorage.getItem('sams_refresh');
    },
    async login(email: string, password: string) {
      const { data } = await api.post('/v1/auth/token/', { email, password });
      this.access = data.access;
      this.refresh = data.refresh;
      localStorage.setItem('sams_access', data.access);
      localStorage.setItem('sams_refresh', data.refresh);
      await this.fetchMe();
    },
    async fetchMe() {
      const { data } = await api.get('/v1/accounts/me/');
      this.user = data;
    },
    logout() {
      this.access = null;
      this.refresh = null;
      this.user = null;
      localStorage.removeItem('sams_access');
      localStorage.removeItem('sams_refresh');
    },
  },
});
