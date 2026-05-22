import type { RouteRecordRaw } from 'vue-router';

const ADMIN = ['admin', 'super_admin'];
const STAFF = ['admin', 'super_admin', 'operations'];
const COACH_PLUS = ['admin', 'super_admin', 'operations', 'coach'];
const ALL = ['admin', 'super_admin', 'operations', 'coach', 'customer'];

const routes: RouteRecordRaw[] = [
  { path: '/login', component: () => import('pages/LoginPage.vue') },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('pages/DashboardPage.vue'), meta: { roles: ALL } },
      { path: 'players', name: 'players', component: () => import('pages/PlayersPage.vue'), meta: { roles: COACH_PLUS } },
      { path: 'coaches', name: 'coaches', component: () => import('pages/CoachesPage.vue'), meta: { roles: STAFF } },
      { path: 'groups', name: 'groups', component: () => import('pages/GroupsPage.vue'), meta: { roles: COACH_PLUS } },
      { path: 'venues', name: 'venues', component: () => import('pages/VenuesPage.vue'), meta: { roles: STAFF } },
      { path: 'sessions', name: 'sessions', component: () => import('pages/SessionsPage.vue'), meta: { roles: COACH_PLUS } },
      { path: 'users', name: 'users', component: () => import('pages/UsersPage.vue'), meta: { roles: ADMIN } },
      { path: 'payments', name: 'payments', component: () => import('pages/PaymentsPage.vue'), meta: { roles: STAFF } },
      { path: 'notifications', name: 'notifications', component: () => import('pages/NotificationsPage.vue'), meta: { roles: ALL } },
      { path: 'my-schedule', name: 'mySchedule', component: () => import('pages/CustomerSchedulePage.vue'), meta: { roles: ['customer'] } },
      { path: 'coach-dashboard', name: 'coachDashboard', component: () => import('pages/CoachDashboardPage.vue'), meta: { roles: ['coach'] } },
      { path: 'loyalty-points', name: 'loyaltyPoints', component: () => import('pages/LoyaltyPointsPage.vue'), meta: { roles: STAFF } },
      { path: 'operations', name: 'operations', component: () => import('pages/OperationsPage.vue'), meta: { roles: STAFF } },
    ],
  },
  { path: '/:catchAll(.*)*', component: () => import('pages/ErrorNotFound.vue') },
];

export default routes;
