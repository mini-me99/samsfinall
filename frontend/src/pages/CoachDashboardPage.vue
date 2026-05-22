<template>
  <q-page class="sams-page">
    <header class="dash__head">
      <div>
        <div class="sams-eyebrow">Coach Portal</div>
        <h1 class="sams-title">Your Players</h1>
        <p class="sams-subtitle">Manage your players, create groups, and schedule sessions.</p>
      </div>
      <q-btn color="primary" icon="refresh" label="Refresh" @click="load" />
    </header>

    <q-tabs v-model="tab" dense align="left" class="q-mb-md">
      <q-tab name="players" label="My Players" />
      <q-tab name="schedule" label="My Schedule" />
      <q-tab name="groups" label="Groups" />
      <q-tab name="sessions" label="Schedule Session" />
      <q-tab name="requests" label="Cancellation Requests" />
    </q-tabs>

    <!-- My Players Tab -->
    <section v-if="tab === 'players'">
      <div class="row q-col-gutter-md">
        <div v-for="p in players" :key="p.id" class="col-12 col-sm-6 col-md-4">
          <q-card class="sams-card" flat bordered>
            <q-card-section>
              <div class="row items-center">
                <q-avatar size="40px" color="primary" text-color="white" class="q-mr-md">
                  {{ p.first_name?.charAt(0) }}{{ p.last_name?.charAt(0) }}
                </q-avatar>
                <div>
                  <div class="text-weight-bold">{{ p.first_name }} {{ p.last_name }}</div>
                  <div class="text-grey-7 text-caption">{{ p.status }}</div>
                </div>
              </div>
              <q-separator class="q-my-sm" />
              <div class="text-caption">
                <div><strong>Preference:</strong> {{ p.preference_type }}</div>
                <div v-if="p.preferred_days?.length"><strong>Days:</strong> {{ p.preferred_days.join(', ') }}</div>
                <div v-if="p.preferred_time"><strong>Time:</strong> {{ p.preferred_time }}</div>
                <div v-if="p.linked_partner_name"><strong>Partner:</strong> {{ p.linked_partner_name }}</div>
              </div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat color="primary" icon="event" label="Schedule" size="sm" @click="openSchedule(p)" />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </section>

    <!-- My Schedule Tab -->
    <section v-if="tab === 'schedule'">
      <div class="row items-center q-mb-md">
        <div class="text-h6 col">My Schedule</div>
        <q-btn flat color="primary" icon="refresh" size="sm" @click="loadMySchedule" />
      </div>
      <div v-if="mySessions.length === 0" class="text-center text-grey q-pa-xl">
        <q-icon name="event_busy" size="48px" />
        <p>No upcoming sessions</p>
      </div>
      <div v-else class="q-gutter-sm">
        <div v-for="(day, dayIdx) in groupedSessions" :key="dayIdx">
          <div class="text-subtitle2 text-weight-bold q-mt-md q-mb-sm" style="color: var(--sams-accent)">
            {{ day.date }}
          </div>
          <q-card v-for="s in day.sessions" :key="s.id" class="sams-card" flat bordered style="padding: 14px 18px">
            <div class="row items-center">
              <div class="col-2 text-center">
                <div class="text-h5 text-weight-bold" style="color: var(--sams-accent); font-family: 'Space Grotesk', sans-serif">
                  {{ formatTime(s.starts_at) }}
                </div>
                <div class="text-caption text-grey-5">{{ formatEndTime(s.starts_at, s.ends_at) }}</div>
              </div>
              <div class="col-7">
                <div class="text-weight-bold">{{ s.title }}</div>
                <div class="text-caption text-grey-5">
                  <q-icon name="people" size="14px" class="q-mr-xs" />
                  {{ s.enrolled_count || 0 }} enrolled
                  <q-icon name="place" size="14px" class="q-ml-md q-mr-xs" />
                  {{ s.venue_name || 'No venue' }}
                </div>
              </div>
              <div class="col-3 text-right">
                <q-chip :color="s.status === 'scheduled' ? 'positive' : 'grey'" text-color="white" dense>
                  {{ s.status }}
                </q-chip>
              </div>
            </div>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Groups Tab -->
    <section v-if="tab === 'groups'">
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Create Group</q-card-section>
            <q-card-section class="q-gutter-sm">
              <q-input v-model="groupForm.name" label="Group name" filled />
              <div class="row q-col-gutter-sm">
                <q-input class="col" v-model="groupForm.age_min" type="number" label="Min age" filled />
                <q-input class="col" v-model="groupForm.age_max" type="number" label="Max age" filled />
              </div>
              <q-input v-model="groupForm.capacity" type="number" label="Capacity" filled :min="1" />
              <q-select v-model="groupForm.members" :options="allPlayers" option-value="id" option-label="fullName" label="Add players" multiple filled use-chips use-input input-debounce="300" @filter="filterGroupPlayers">
                <template v-slot:no-option><q-item><q-item-section class="text-grey">Type to search</q-item-section></q-item></template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label>{{ scope.opt.fullName }}</q-item-label>
                      <q-item-label caption class="text-grey-5">
                        {{ scope.opt.preference_type }} | {{ (scope.opt.preferred_days || []).join(', ') }} | {{ scope.opt.preferred_time || '--:--' }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn color="primary" label="Create Group" :loading="creatingGroup" @click="createGroup" />
            </q-card-actions>
          </q-card>
        </div>
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Your Groups ({{ myGroups.length }})</q-card-section>
            <q-list bordered separator>
              <q-item v-for="g in myGroups" :key="g.id">
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ g.name }}</q-item-label>
                  <q-item-label caption>{{ g.member_count || 0 }} members</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-btn flat dense color="primary" icon="event" label="Schedule" size="sm" @click="scheduleForGroup(g)" />
                </q-item-section>
              </q-item>
              <q-item v-if="myGroups.length === 0">
                <q-item-section class="text-grey text-center">No groups yet</q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Schedule Session Tab -->
    <section v-if="tab === 'sessions'">
      <q-card class="sams-card" flat bordered>
        <q-card-section class="text-h6">Create Session</q-card-section>
        <q-card-section class="q-gutter-sm">
          <q-input v-model="sessionForm.title" label="Session Title" filled />
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="sessionForm.starts_at" type="datetime-local" label="Start" filled />
            <q-input class="col" v-model="sessionForm.ends_at" type="datetime-local" label="End" filled />
          </div>
          <q-select v-model="sessionForm.players" :options="allPlayers" option-value="id" option-label="fullName" label="Select Players" multiple filled use-chips />
          <q-select v-model="sessionForm.venue" :options="venues" option-value="id" option-label="name" label="Venue" filled clearable />
          <q-input v-model="sessionForm.capacity" type="number" label="Capacity" filled :min="1" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="Create Session" :loading="saving" @click="createSession" />
        </q-card-actions>
      </q-card>
    </section>

    <!-- Cancellation Requests Tab -->
    <section v-if="tab === 'requests'">
      <div class="q-gutter-sm">
        <q-card v-for="r in cancelRequests" :key="r.id" class="sams-card" flat bordered>
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-weight-bold">{{ r.occurrence_title || 'Session' }}</div>
                <div class="text-caption text-grey-5">{{ r.occurrence_time }}</div>
              </div>
              <q-chip :color="statusChipColor(r.status)" text-color="white" dense>{{ r.status.replace('_',' ') }}</q-chip>
            </div>
            <q-separator class="q-my-sm" />
            <div class="text-caption">
              <div><strong>Player:</strong> {{ r.requester_name }}</div>
              <div><strong>Reason:</strong> {{ r.reason }}</div>
            </div>
          </q-card-section>
          <q-card-actions v-if="r.status === 'coach_review'" align="right">
            <q-input v-model="reviewNotes[r.id]" label="Coach notes (optional)" dense filled class="q-mr-sm" style="flex:1" />
            <q-btn flat color="positive" icon="check" label="Approve" size="sm" @click="reviewCancel(r.id, 'approve')" />
            <q-btn flat color="negative" icon="close" label="Reject" size="sm" @click="reviewCancel(r.id, 'reject')" />
          </q-card-actions>
        </q-card>
      </div>
      <div v-if="cancelRequests.length === 0" class="text-center text-grey q-pa-xl">
        <q-icon name="check_circle" size="48px" />
        <p>No pending cancellation requests</p>
      </div>
    </section>

    <!-- Schedule individual dialog -->
    <q-dialog v-model="scheduleDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section class="text-h6">Schedule for {{ schedulePlayer?.first_name }} {{ schedulePlayer?.last_name }}</q-card-section>
        <q-card-section class="q-gutter-sm">
          <q-input v-model="singleForm.title" label="Session Title" filled />
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="singleForm.starts_at" type="datetime-local" label="Start" filled />
            <q-input class="col" v-model="singleForm.ends_at" type="datetime-local" label="End" filled />
          </div>
          <q-select v-model="singleForm.venue" :options="venues" option-value="id" option-label="name" label="Venue" filled clearable />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Create" :loading="savingSingle" @click="createIndividualSession" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import { useAuthStore } from 'src/stores/auth';

const $q = useQuasar();
const auth = useAuthStore();
const tab = ref('players');
const players = ref<any[]>([]);
const allPlayers = ref<any[]>([]);
const venues = ref<any[]>([]);
const cancelRequests = ref<any[]>([]);
const mySessions = ref<any[]>([]);
const myGroups = ref<any[]>([]);
const saving = ref(false);
const savingSingle = ref(false);
const creatingGroup = ref(false);
const reviewNotes = ref<Record<string, string>>({});
const scheduleDialog = ref(false);
const schedulePlayer = ref<any>(null);
const scheduleGroup = ref<any>(null);
const coachId = ref<string | null>(null);

const sessionForm = ref({
  title: '',
  starts_at: '',
  ends_at: '',
  players: [] as any[],
  group: null as any,
  venue: null as any,
  capacity: 20,
});

const singleForm = ref({
  title: '',
  starts_at: '',
  ends_at: '',
  venue: null as any,
});

const groupForm = ref({
  name: '',
  age_min: 4,
  age_max: 18,
  capacity: 20,
  members: [] as any[],
});

async function load() {
  try {
    // Get coach profile for current user
    const me = auth.user;
    if (me) {
      const coachesResp = await api.get('/v1/coaches/', { params: { user: me.id } }).catch(() => ({ data: { results: [] } }));
      const coaches = Array.isArray(coachesResp.data) ? coachesResp.data : (coachesResp.data.results || []);
      if (coaches.length > 0) {
        coachId.value = coaches[0].id;
      }
    }

    if (!coachId.value) {
      $q.notify({ type: 'warning', message: 'No coach profile linked to your account. An admin/operations user must link your coach profile first.' });
      return;
    }

    // Get linked players
    const linksResp = await api.get('/v1/players/coach-links/', { params: { coach: coachId.value, page_size: 500 } }).catch(() => ({ data: { results: [] } }));
    const linkResults = Array.isArray(linksResp.data) ? linksResp.data : (linksResp.data.results || []);
    const playerIds = linkResults.map((l: any) => l.player);
    if (playerIds.length > 0) {
      const playersResp = await api.get('/v1/players/', { params: { page_size: 500 } }).catch(() => ({ data: { results: [] } }));
      const pResults = Array.isArray(playersResp.data) ? playersResp.data : (playersResp.data.results || []);
      players.value = pResults.filter((p: any) => playerIds.includes(p.id));
      allPlayers.value = players.value.map((p: any) => ({ ...p, fullName: `${p.first_name} ${p.last_name}` }));
    }

    // Get venues
    const vResp = await api.get('/v1/sessions/venues/', { params: { page_size: 200 } }).catch(() => ({ data: { results: [] } }));
    venues.value = Array.isArray(vResp.data) ? vResp.data : (vResp.data.results || []);

    // Get cancellation requests filtered by this coach
    const crResp = await api.get('/v1/players/cancellation-requests/', { params: { coach: coachId.value, page_size: 100 } }).catch(() => ({ data: { results: [] } }));
    cancelRequests.value = Array.isArray(crResp.data) ? crResp.data : (crResp.data.results || []);
  } catch (e: any) {
    // Silent fail - partial data still works
  }
}

function openSchedule(player: any) {
  schedulePlayer.value = player;
  singleForm.value = { title: `Session with ${player.first_name}`, starts_at: '', ends_at: '', venue: null };
  scheduleDialog.value = true;
}

async function createIndividualSession() {
  savingSingle.value = true;
  try {
    // Create an occurrence directly
    const payload: any = {
      title: singleForm.value.title,
      starts_at: singleForm.value.starts_at,
      ends_at: singleForm.value.ends_at,
      venue_id: singleForm.value.venue?.id || null,
      capacity: 1,
    };
    if (coachId.value) payload.coaches_ids = [coachId.value];
    const { data: occ } = await api.post('/v1/sessions/occurrences/', payload);
    // Enroll the player
    await api.post('/v1/sessions/enrollments/', {
      occurrence: occ.id,
      player: schedulePlayer.value.id,
    });
    $q.notify({ type: 'positive', message: 'Session created and player enrolled' });
    scheduleDialog.value = false;
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to create session' });
  } finally {
    savingSingle.value = false;
  }
}

async function createSession() {
  saving.value = true;
  try {
    const payload: any = {
      title: sessionForm.value.title,
      starts_at: sessionForm.value.starts_at,
      ends_at: sessionForm.value.ends_at,
      venue_id: sessionForm.value.venue?.id || null,
      capacity: sessionForm.value.capacity || 20,
    };
    if (coachId.value) payload.coaches_ids = [coachId.value];
    const { data: occ } = await api.post('/v1/sessions/occurrences/', payload);
    // Enroll all selected players
    for (const p of sessionForm.value.players) {
      await api.post('/v1/sessions/enrollments/', {
        occurrence: occ.id,
        player: p.id,
      });
    }
    $q.notify({ type: 'positive', message: `Session created with ${sessionForm.value.players.length} players` });
    sessionForm.value = { title: '', starts_at: '', ends_at: '', players: [], venue: null, capacity: 20 };
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to create session' });
  } finally {
    saving.value = false;
  }
}

function statusChipColor(s: string) {
  if (s === 'coach_review') return 'warning';
  if (s === 'approved') return 'positive';
  if (s === 'rejected') return 'negative';
  return 'grey';
}

async function reviewCancel(id: string, action: string) {
  try {
    await api.post(`/v1/players/cancellation-requests/${id}/review/`, {
      action,
      coach_id: coachId.value,
      notes: reviewNotes.value[id] || '',
    });
    $q.notify({ type: 'positive', message: `Cancellation ${action}d. Notification sent.` });
    delete reviewNotes.value[id];
    await load();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to update' });
  }
}

async function loadMySchedule() {
  if (!coachId.value) return;
  const resp = await api.get('/v1/sessions/occurrences/', {
    params: { coaches: coachId.value, ordering: 'starts_at', page_size: 50 },
  }).catch(() => ({ data: { results: [] } }));
  const results = Array.isArray(resp.data) ? resp.data : (resp.data.results || []);
  const now = new Date().toISOString();
  mySessions.value = results
    .filter((s: any) => s.starts_at >= now && s.status === 'scheduled')
    .sort((a: any, b: any) => a.starts_at.localeCompare(b.starts_at));
}

async function loadMyGroups() {
  if (!coachId.value) return;
  const resp = await api.get('/v1/groups/', { params: { primary_coach: coachId.value, page_size: 100 } }).catch(() => ({ data: { results: [] } }));
  const results = Array.isArray(resp.data) ? resp.data : (resp.data.results || []);
  // Get member counts
  myGroups.value = await Promise.all(results.map(async (g: any) => {
    const mResp = await api.get('/v1/groups/memberships/', { params: { group: g.id, page_size: 500 } }).catch(() => ({ data: { results: [] } }));
    const members = Array.isArray(mResp.data) ? mResp.data : (mResp.data.results || []);
    return { ...g, member_count: members.length };
  }));
}

async function createGroup() {
  if (!groupForm.value.name) {
    $q.notify({ type: 'warning', message: 'Group name is required' });
    return;
  }
  creatingGroup.value = true;
  try {
    const payload: any = {
      name: groupForm.value.name,
      age_min: groupForm.value.age_min,
      age_max: groupForm.value.age_max,
      capacity: groupForm.value.capacity,
      primary_coach: coachId.value,
    };
    const { data: group } = await api.post('/v1/groups/', payload);
    // Add members
    for (const p of groupForm.value.members) {
      await api.post('/v1/groups/memberships/', { group: group.id, player: p.id });
    }
    $q.notify({ type: 'positive', message: `Group "${group.name}" created with ${groupForm.value.members.length} members` });
    groupForm.value = { name: '', age_min: 4, age_max: 18, capacity: 20, members: [] };
    await loadMyGroups();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to create group' });
  } finally {
    creatingGroup.value = false;
  }
}

function scheduleForGroup(g: any) {
  tab.value = 'sessions';
  sessionForm.value.group = g;
  sessionForm.value.title = `${g.name} Session`;
  sessionForm.value.players = [];
  $q.notify({ type: 'info', message: `Scheduling for group: ${g.name}` });
}

function filterGroupPlayers(val: string, update: (fn: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    allPlayers.value = players.value.filter((p: any) =>
      !needle || (p.first_name + ' ' + p.last_name + ' ' + (p.phone || '')).toLowerCase().includes(needle)
    );
  });
}

const groupedSessions = computed(() => {
  const groups: Record<string, any[]> = {};
  for (const s of mySessions.value) {
    const d = new Date(s.starts_at).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    if (!groups[d]) groups[d] = [];
    groups[d].push(s);
  }
  return Object.entries(groups).map(([date, sessions]) => ({ date, sessions }));
});

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
}

function formatEndTime(start: string, end: string) {
  return `${new Date(start).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })} - ${new Date(end).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })}`;
}

// Extend load to also fetch schedule and groups
const origLoad = load;
load = async function() {
  await origLoad();
  if (coachId.value) {
    await Promise.all([loadMySchedule(), loadMyGroups()]);
  }
} as any;

onMounted(load);
</script>

<style scoped lang="scss">
.dash__head {
  display: flex; align-items: flex-end; justify-content: space-between;
  gap: 16px; margin-bottom: 24px;
}
.sams-card { border-radius: 12px; }
</style>