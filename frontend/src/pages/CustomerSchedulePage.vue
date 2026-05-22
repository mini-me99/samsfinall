<template>
  <q-page class="sams-page">
    <header class="dash__head">
      <div>
        <div class="sams-eyebrow">My Account</div>
        <h1 class="sams-title">Your Sessions</h1>
        <p class="sams-subtitle">View your schedule, streak, and rewards.</p>
      </div>
    </header>

    <!-- Streak & Points Cards -->
    <section class="row q-col-gutter-md q-mb-lg">
      <div class="col-12 col-sm-4">
        <q-card class="sams-card" flat bordered>
          <q-card-section class="text-center">
            <q-icon name="local_fire_department" size="40px" color="orange" />
            <div class="text-h4 text-weight-bold">{{ streak.current }}</div>
            <div class="text-caption text-grey">Day Streak</div>
            <div class="text-caption">Longest: {{ streak.longest }}</div>
            <q-btn v-if="streak.current > 0" flat color="orange" icon="share" label="Share Story" size="sm" @click="shareStreak" class="q-mt-sm" />
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-4">
        <q-card class="sams-card" flat bordered>
          <q-card-section class="text-center">
            <q-icon name="stars" size="40px" color="yellow-8" />
            <div class="text-h4 text-weight-bold">{{ totalPoints }}</div>
            <div class="text-caption text-grey">Loyalty Points</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-4">
        <q-card class="sams-card" flat bordered>
          <q-card-section class="text-center">
            <q-icon name="pending_actions" size="40px" color="primary" />
            <div class="text-h4 text-weight-bold">{{ upcomingCount }}</div>
            <div class="text-caption text-grey">Upcoming Sessions</div>
          </q-card-section>
        </q-card>
      </div>
    </section>

    <div class="row items-center q-mb-md">
      <div class="text-h6">Session Schedule</div>
      <q-space />
      <q-input v-model="fromDate" type="date" dense filled label="From" class="q-mr-sm" style="width:160px" />
      <q-input v-model="toDate" type="date" dense filled label="To" style="width:160px" />
      <q-btn color="primary" icon="refresh" label="Load" @click="load" />
    </div>

    <section v-if="loading" class="q-pa-md text-center">
      <q-spinner size="40px" />
    </section>

    <section v-else-if="sessions.length === 0" class="q-pa-md text-center">
      <q-icon name="event_busy" size="64px" color="grey-5" />
      <p class="text-grey-6 q-mt-md">No sessions found for this period.</p>
    </section>

    <section v-else class="q-gutter-sm">
      <q-card v-for="s in sessions" :key="s.id" class="sams-card" flat bordered>
        <q-card-section>
          <div class="row items-center">
            <div class="col">
              <div class="text-h6">{{ s.title }}</div>
              <div class="text-grey-7 q-mt-xs">
                <q-icon name="schedule" size="16px" class="q-mr-xs" />
                {{ formatDate(s.starts_at) }} — {{ formatTime(s.starts_at) }} to {{ formatTime(s.ends_at) }}
              </div>
              <div v-if="s.venue" class="text-grey-7">
                <q-icon name="place" size="16px" class="q-mr-xs" />
                {{ s.venue }}
              </div>
              <div v-if="s.group" class="text-grey-7">
                <q-icon name="group" size="16px" class="q-mr-xs" />
                {{ s.group }}
              </div>
            </div>
            <div class="col-auto">
              <q-chip :color="statusColor(s.status)" text-color="white" dense>
                {{ s.status }}
              </q-chip>
            </div>
          </div>
        </q-card-section>
        <q-card-actions v-if="canCancel(s)" align="right">
          <q-btn flat color="negative" icon="cancel" label="Request Cancellation" size="sm" @click="openCancelDialog(s)" />
        </q-card-actions>
      </q-card>
    </section>

    <!-- Cancellation dialog -->
    <q-dialog v-model="cancelDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section class="text-h6">Request Cancellation</q-card-section>
        <q-card-section>
          <p>Cancel <strong>{{ cancelSession?.title }}</strong> on {{ formatDate(cancelSession?.starts_at) }}?</p>
          <q-input v-model="cancelReason" type="textarea" label="Reason" filled autogrow />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Close" v-close-popup />
          <q-btn color="negative" label="Request Cancellation" :loading="cancelling" @click="submitCancellation" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';

const $q = useQuasar();
const loading = ref(false);
const sessions = ref<any[]>([]);
const streak = ref({ current: 0, longest: 0 });
const totalPoints = ref(0);
const upcomingCount = ref(0);
const now = new Date();
const fromDate = ref(now.toISOString().slice(0, 10));
const in30 = new Date(Date.now() + 30 * 86400000);
const toDate = ref(in30.toISOString().slice(0, 10));
const cancelDialog = ref(false);
const cancelSession = ref<any>(null);
const cancelReason = ref('');
const cancelling = ref(false);
const streakShareUrl = ref('');

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString();
}
function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function statusColor(s: string) {
  if (s === 'scheduled') return 'positive';
  if (s === 'cancelled') return 'negative';
  if (s === 'completed') return 'grey';
  return 'grey';
}
function canCancel(s: any) {
  return s.status === 'scheduled';
}
function openCancelDialog(s: any) {
  cancelSession.value = s;
  cancelReason.value = '';
  cancelDialog.value = true;
}
async function submitCancellation() {
  if (!cancelReason.value) {
    $q.notify({ type: 'warning', message: 'Please provide a reason' });
    return;
  }
  cancelling.value = true;
  try {
    await api.post('/v1/players/cancellation-requests/', {
      occurrence: cancelSession.value.id,
      reason: cancelReason.value,
    });
    $q.notify({ type: 'positive', message: 'Cancellation request submitted' });
    cancelDialog.value = false;
    await load();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to submit' });
  } finally {
    cancelling.value = false;
  }
}
function shareStreak() {
  const text = `I'm on a ${streak.value.current}-day attendance streak at SAMS! 🔥`;
  const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

async function load() {
  loading.value = true;
  try {
    const [schedRes, dashRes] = await Promise.all([
      api.get('/v1/players/my-schedule/', { params: { from: fromDate.value, to: toDate.value } }),
      api.get('/v1/players/my-dashboard/').catch(() => ({ data: {} })),
    ]);
    sessions.value = schedRes.data;
    const dash = dashRes.data;
    if (dash.streak) {
      streak.value = dash.streak;
    }
    totalPoints.value = dash.total_points || 0;
    upcomingCount.value = dash.upcoming_sessions?.length || 0;
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to load schedule' });
  } finally {
    loading.value = false;
  }
}
onMounted(load);
</script>

<style scoped lang="scss">
.dash__head {
  display: flex; align-items: flex-end; justify-content: space-between;
  gap: 16px; margin-bottom: 24px; flex-wrap: wrap;
}
.sams-card { border-radius: 12px; }
</style>