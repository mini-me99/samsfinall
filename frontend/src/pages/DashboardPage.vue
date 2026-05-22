<template>
  <q-page class="sams-page dash">
    <header class="dash__head">
      <div>
        <div class="sams-eyebrow">Control room</div>
        <h1 class="sams-title">Good {{ partOfDay }}{{ auth.user?.first_name ? `, ${auth.user.first_name}` : '' }}.</h1>
        <p class="sams-subtitle">Here's how your academy is performing right now.</p>
      </div>
      <div class="dash__chip">
        <span class="dash__chipDot" />
        Live — synced just now
      </div>
    </header>

    <section class="dash__kpis">
      <article
        v-for="kpi in kpis"
        :key="kpi.label"
        class="kpi"
        :class="{ 'kpi--hero': kpi.hero }"
      >
        <div class="kpi__top">
          <q-icon :name="kpi.icon" size="18px" class="kpi__icon" />
          <div class="kpi__label">{{ kpi.label }}</div>
        </div>
        <div class="kpi__value">{{ kpi.value }}</div>
        <div class="kpi__delta" :class="kpi.tone">
          <q-icon :name="kpi.tone === 'good' ? 'trending_up' : 'trending_flat'" size="14px" />
          {{ kpi.delta }}
        </div>
      </article>
    </section>

    <section class="dash__grid">
      <div class="sams-card dash__panel">
        <div class="dash__panelHead">
          <div>
            <div class="sams-eyebrow">Activity</div>
            <h3 class="dash__panelTitle">This week at a glance</h3>
          </div>
        </div>
        <div class="dash__bars">
          <div
            v-for="(d, i) in week"
            :key="i"
            class="dash__bar"
            :style="{ height: `${d.h}%` }"
            :title="`${d.label}: ${d.h}% attendance`"
          >
            <span>{{ d.label }}</span>
          </div>
        </div>
      </div>

      <div class="sams-card dash__panel">
        <div class="dash__panelHead">
          <div>
            <div class="sams-eyebrow">Today</div>
            <h3 class="dash__panelTitle">Upcoming sessions</h3>
          </div>
        </div>
        <ul class="dash__list">
          <li v-for="s in upcoming" :key="s.id">
            <div class="dash__listTime">{{ s.time }}</div>
            <div class="dash__listBody">
              <div class="dash__listTitle">{{ s.title }}</div>
              <div class="dash__listSub">{{ s.coach }} · {{ s.venue }}</div>
            </div>
            <q-chip dense :color="s.tone" text-color="white" class="dash__listChip">
              {{ s.status }}
            </q-chip>
          </li>
        </ul>
      </div>
    </section>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { api } from 'src/boot/axios';
import { useAuthStore } from 'src/stores/auth';

const auth = useAuthStore();
interface Dash {
  active_players?: number;
  sessions_this_week?: number;
  attendance_rate?: number;
  outstanding_amount?: number;
  revenue_last_30_days?: number;
}
const data = ref<Dash | null>(null);

onMounted(async () => {
  try {
    const r = await api.get('/v1/analytics/dashboard/');
    data.value = r.data;
  } catch {/* noop */}
});

const partOfDay = computed(() => {
  const h = new Date().getHours();
  if (h < 12) return 'morning';
  if (h < 18) return 'afternoon';
  return 'evening';
});

const role = computed(() => auth.user?.role ?? 'customer');

const kpis = computed(() => {
  const r = role.value;
  if (r === 'customer') {
    return [
      { label: 'My upcoming sessions', icon: 'event', value: data.value?.sessions_this_week ?? '—',
        delta: 'This week', tone: 'mute', hero: true },
      { label: 'Attendance',           icon: 'check_circle',
        value: data.value ? `${data.value.attendance_rate ?? 0}%` : '—',
        delta: 'Your record', tone: 'good' },
      { label: 'Outstanding',          icon: 'receipt_long',
        value: data.value ? `${data.value.outstanding_amount ?? 0} EGP` : '—',
        delta: 'Open invoices', tone: 'mute' },
    ];
  }
  if (r === 'coach') {
    return [
      { label: 'My players',         icon: 'groups', value: data.value?.active_players ?? '—',
        delta: 'Across your groups', tone: 'good', hero: true },
      { label: 'Sessions this week', icon: 'event',  value: data.value?.sessions_this_week ?? '—',
        delta: 'On schedule', tone: 'mute' },
      { label: 'Attendance rate',    icon: 'check_circle',
        value: data.value ? `${data.value.attendance_rate}%` : '—',
        delta: 'Last 7 days', tone: 'good' },
    ];
  }
  // admin / super_admin / operations
  return [
    { label: 'Active players',     icon: 'groups', value: data.value?.active_players ?? '—',
      delta: '+12 this month', tone: 'good', hero: true },
    { label: 'Sessions this week', icon: 'event',  value: data.value?.sessions_this_week ?? '—',
      delta: 'On schedule', tone: 'mute' },
    { label: 'Attendance rate',    icon: 'check_circle',
      value: data.value ? `${data.value.attendance_rate}%` : '—',
      delta: '+3.4% vs last week', tone: 'good' },
    { label: 'Outstanding',        icon: 'receipt_long',
      value: data.value ? `${data.value.outstanding_amount} EGP` : '—',
      delta: '8 invoices open', tone: 'mute' },
    ...(r !== 'operations' ? [{ label: 'Revenue (30d)', icon: 'paid',
      value: data.value ? `${data.value.revenue_last_30_days} EGP` : '—',
      delta: '+18.2% MoM', tone: 'good' }] : []),
  ];
});

const week = [
  { label: 'Mon', h: 64 }, { label: 'Tue', h: 78 }, { label: 'Wed', h: 52 },
  { label: 'Thu', h: 88 }, { label: 'Fri', h: 71 }, { label: 'Sat', h: 94 }, { label: 'Sun', h: 40 },
];

const upcoming = [
  { id: 1, time: '16:00', title: 'U12 Tactics',  coach: 'Coach Ahmed',  venue: 'Pitch A', status: 'Confirmed', tone: 'positive' },
  { id: 2, time: '17:30', title: 'Goalkeeping',  coach: 'Coach Sara',   venue: 'Pitch B', status: 'Confirmed', tone: 'positive' },
  { id: 3, time: '19:00', title: 'U16 Match',    coach: 'Coach Omar',   venue: 'Main',    status: 'Pending',   tone: 'warning' },
];
</script>

<style scoped lang="scss">
.dash { max-width: 1280px; margin: 0 auto; }
.dash__head {
  display: flex; align-items: flex-end; justify-content: space-between;
  gap: 16px; margin-bottom: 24px;
}
.dash__chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 14px; border-radius: 999px;
  background: var(--sams-surface);
  border: 1px solid var(--sams-border-strong);
  font-size: 12px; color: var(--sams-text-dim);
}
.dash__chipDot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--sams-good);
  box-shadow: 0 0 10px var(--sams-good);
}

.dash__kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 16px;
}
.kpi {
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0)) , var(--sams-surface);
  border: 1px solid var(--sams-border);
  border-radius: 16px;
  padding: 18px 18px 16px;
  position: relative;
  overflow: hidden;
  transition: transform .25s ease, border-color .25s ease;
}
.kpi:hover { transform: translateY(-2px); border-color: var(--sams-border-strong); }
.kpi--hero {
  background:
    radial-gradient(120% 100% at 0% 0%, rgba(198,242,78,0.18), transparent 60%),
    linear-gradient(180deg, rgba(198,242,78,0.06), rgba(198,242,78,0)) , var(--sams-surface);
  border-color: rgba(198,242,78,0.28);
}
.kpi__top { display: flex; align-items: center; gap: 8px; color: var(--sams-text-dim); }
.kpi__icon { color: var(--sams-accent); }
.kpi__label { font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; }
.kpi__value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 36px; font-weight: 600; letter-spacing: -0.02em;
  margin: 10px 0 6px; color: var(--sams-text);
}
.kpi__delta { font-size: 12.5px; color: var(--sams-text-mute); display: inline-flex; align-items: center; gap: 4px; }
.kpi__delta.good { color: var(--sams-good); }

.dash__grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
  @media (max-width: 1000px) { grid-template-columns: 1fr; }
}
.dash__panelHead { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.dash__panelTitle { font-size: 18px; margin: 4px 0 0; }

.dash__bars {
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 12px; height: 220px; align-items: end;
  padding-top: 8px;
}
.dash__bar {
  position: relative;
  background: linear-gradient(180deg, var(--sams-accent), rgba(198,242,78,0.15));
  border-radius: 8px 8px 4px 4px;
  min-height: 6%;
  transition: filter .25s ease;
}
.dash__bar:hover { filter: brightness(1.1); }
.dash__bar span {
  position: absolute; bottom: -22px; left: 50%; transform: translateX(-50%);
  font-size: 11px; color: var(--sams-text-mute); letter-spacing: 0.04em;
}

.dash__list { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.dash__list li {
  display: grid;
  grid-template-columns: 56px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--sams-border);
  border-radius: 12px;
  background: var(--sams-surface-2);
}
.dash__listTime {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600; color: var(--sams-accent);
}
.dash__listTitle { font-weight: 600; color: var(--sams-text); }
.dash__listSub { font-size: 12px; color: var(--sams-text-mute); margin-top: 2px; }
.dash__listChip { font-size: 10.5px; letter-spacing: 0.04em; }
</style>
