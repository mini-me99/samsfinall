<template>
  <q-layout view="hHh Lpr lff">
    <q-header class="sams-header">
      <q-toolbar class="sams-toolbar">
        <q-btn flat dense round icon="menu" @click="drawer = !drawer" class="lt-md" />
        <div class="sams-mark">
          <span class="sams-mark__dot" />
          <span>SAMS</span>
        </div>

        <q-space />

        <div class="sams-header__user" v-if="auth.user">
          <q-avatar size="32px" class="sams-avatar">
            {{ initials }}
          </q-avatar>
          <div class="sams-header__meta">
            <div class="sams-header__name">{{ displayName }}</div>
            <div class="sams-header__role">{{ roleLabel }}</div>
          </div>
        </div>
        <q-btn flat dense round icon="logout" @click="logout">
          <q-tooltip>Sign out</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="drawer"
      show-if-above
      :width="248"
      :breakpoint="900"
      class="sams-drawer"
    >
      <div class="sams-drawer__inner">
        <div class="sams-drawer__section">Main</div>
        <q-list padding>
          <q-item
            v-for="item in visibleNav"
            :key="item.to"
            clickable
            :to="item.to"
            exact
            v-ripple
          >
            <q-item-section avatar>
              <q-icon :name="item.icon" size="20px" />
            </q-item-section>
            <q-item-section>{{ item.label }}</q-item-section>
          </q-item>
        </q-list>

        <div class="sams-drawer__foot">
          <div class="sams-drawer__pulse">
            <div class="sams-eyebrow">Live</div>
            <div class="sams-drawer__pulseTitle">All systems normal</div>
            <div class="sams-drawer__pulseSub">Last sync just now</div>
          </div>
        </div>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'src/stores/auth';

const drawer = ref(false);
const router = useRouter();
const auth = useAuthStore();

interface NavItem { to: string; icon: string; label: string; roles: string[] }
const ADMIN = ['admin', 'super_admin'];
const STAFF = ['admin', 'super_admin', 'operations'];
const COACH_PLUS = ['admin', 'super_admin', 'operations', 'coach'];
const ALL = ['admin', 'super_admin', 'operations', 'coach', 'customer'];
const nav: NavItem[] = [
  { to: '/', icon: 'space_dashboard', label: 'Dashboard', roles: ALL },
  { to: '/my-schedule', icon: 'calendar_month', label: 'My Schedule', roles: ['customer'] },
  { to: '/coach-dashboard', icon: 'sports_soccer', label: 'Coach Portal', roles: ['coach'] },
  { to: '/players', icon: 'groups', label: 'Players', roles: COACH_PLUS },
  { to: '/coaches', icon: 'sports', label: 'Coaches', roles: STAFF },
  { to: '/groups', icon: 'category', label: 'Groups', roles: COACH_PLUS },
  { to: '/venues', icon: 'place', label: 'Venues', roles: STAFF },
  { to: '/sessions', icon: 'event', label: 'Sessions', roles: COACH_PLUS },
  { to: '/operations', icon: 'settings', label: 'Operations', roles: STAFF },
  { to: '/loyalty-points', icon: 'stars', label: 'Loyalty Points', roles: STAFF },
  { to: '/users', icon: 'manage_accounts', label: 'Users', roles: ADMIN },
  { to: '/payments', icon: 'payments', label: 'Payments', roles: STAFF },
  { to: '/notifications', icon: 'notifications', label: 'Notifications', roles: ALL },
];

const visibleNav = computed(() =>
  nav.filter((n) => auth.user && n.roles.includes(auth.user.role)),
);

const displayName = computed(() => {
  const u = auth.user;
  if (!u) return '';
  const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.trim();
  return full || u.email;
});

const initials = computed(() => {
  const u = auth.user;
  if (!u) return '?';
  const a = (u.first_name ?? '').charAt(0);
  const b = (u.last_name ?? '').charAt(0);
  const i = (a + b).toUpperCase();
  return i || (u.email?.charAt(0).toUpperCase() ?? '?');
});

const roleLabel = computed(() => {
  const r = auth.user?.role;
  if (!r) return '';
  return r.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase());
});

onMounted(async () => {
  if (auth.isAuthenticated && !auth.user) {
    try { await auth.fetchMe(); } catch {/* noop */}
  }
});

function logout() {
  auth.logout();
  void router.push('/login');
}
</script>

<style scoped lang="scss">
.sams-toolbar {
  min-height: 64px;
  padding: 0 22px;
  gap: 14px;
}

.sams-header__user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  margin-right: 6px;
  border: 1px solid var(--sams-border);
  background: var(--sams-surface);
  border-radius: 999px;
}
.sams-avatar {
  background: linear-gradient(135deg, var(--sams-accent), var(--sams-accent-2));
  color: var(--sams-accent-ink);
  font-weight: 700;
  font-family: 'Space Grotesk', sans-serif;
}
.sams-header__meta { line-height: 1.1; }
.sams-header__name { font-size: 13px; font-weight: 600; color: var(--sams-text); }
.sams-header__role {
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--sams-text-mute);
}

.sams-drawer__inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 18px 4px 18px;
}
.sams-drawer__section {
  padding: 6px 22px 8px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 10.5px;
  color: var(--sams-text-mute);
  font-weight: 600;
}
.sams-drawer__foot { margin-top: auto; padding: 12px; }
.sams-drawer__pulse {
  border: 1px solid var(--sams-border);
  background: linear-gradient(180deg, rgba(198,242,78,0.06), rgba(198,242,78,0));
  border-radius: 14px;
  padding: 14px 14px 16px;
}
.sams-drawer__pulseTitle {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 14px;
  margin-top: 4px;
  color: var(--sams-text);
}
.sams-drawer__pulseSub { font-size: 11.5px; color: var(--sams-text-mute); margin-top: 2px; }
</style>
