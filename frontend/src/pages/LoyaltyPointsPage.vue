<template>
  <q-page class="sams-page">
    <header class="dash__head">
      <div>
        <div class="sams-eyebrow">Rewards</div>
        <h1 class="sams-title">Loyalty Points & Referrals</h1>
        <p class="sams-subtitle">Award points to players and manage referral codes.</p>
      </div>
    </header>

    <q-tabs v-model="tab" dense align="left" class="q-mb-md">
      <q-tab name="points" label="Award Points" />
      <q-tab name="history" label="Points History" />
      <q-tab name="referrals" label="Referral Codes" />
    </q-tabs>

    <!-- Award Points Tab -->
    <section v-if="tab === 'points'" class="row q-col-gutter-md">
      <div class="col-12 col-md-6">
        <q-card class="sams-card" flat bordered>
          <q-card-section class="text-h6">Award Points</q-card-section>
          <q-card-section class="q-gutter-sm">
            <q-select v-model="awardForm.player" :options="players" option-value="id" option-label="fullName" label="Player" filled use-chips />
            <q-input v-model="awardForm.points" type="number" label="Points" filled :min="1" />
            <q-input v-model="awardForm.reason" label="Reason" filled placeholder="e.g. Perfect attendance, Referral bonus, etc." />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn color="primary" label="Award Points" :loading="awarding" @click="awardPoints" />
          </q-card-actions>
        </q-card>
      </div>

      <div class="col-12 col-md-6">
        <q-card class="sams-card" flat bordered>
          <q-card-section class="text-h6">Top Players</q-card-section>
          <q-list bordered separator>
            <q-item v-for="p in topPlayers" :key="p.player__id">
              <q-item-section>
                <q-item-label>{{ p.player_name }}</q-item-label>
                <q-item-label caption>{{ p.total }} points</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="topPlayers.length === 0">
              <q-item-section class="text-grey">No points awarded yet</q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </section>

    <!-- Points History Tab -->
    <section v-if="tab === 'history'">
      <q-table :rows="pointsHistory" :columns="pointsColumns" row-key="id" flat bordered />
    </section>

    <!-- Referrals Tab -->
    <section v-if="tab === 'referrals'">
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Referral Codes</q-card-section>
            <q-table :rows="referrals" :columns="refColumns" row-key="id" flat bordered />
          </q-card>
        </div>
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Award Referral Points</q-card-section>
            <q-card-section class="q-gutter-sm">
              <q-select v-model="refForm.code" :options="referrals" option-value="id" option-label="displayCode" label="Referral Code" filled />
              <q-input v-model="refForm.points" type="number" label="Points" filled :min="1" />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn color="primary" label="Award" :loading="refAwarding" @click="awardReferral" />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </section>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';

const $q = useQuasar();
const tab = ref('points');
const players = ref<any[]>([]);
const topPlayers = ref<any[]>([]);
const pointsHistory = ref<any[]>([]);
const referrals = ref<any[]>([]);
const awarding = ref(false);
const refAwarding = ref(false);

const awardForm = ref({ player: null, points: 10, reason: '' });
const refForm = ref({ code: null, points: 10 });

const pointsColumns = [
  { name: 'player', label: 'Player', field: (r: any) => `${r.player_first_name} ${r.player_last_name}` },
  { name: 'points', label: 'Points', field: 'points' },
  { name: 'reason', label: 'Reason', field: 'reason' },
  { name: 'created_at', label: 'Date', field: (r: any) => new Date(r.created_at).toLocaleDateString() },
];

const refColumns = [
  { name: 'code', label: 'Code', field: 'code' },
  { name: 'user', label: 'User', field: (r: any) => r.user_email || r.user },
  { name: 'points_awarded', label: 'Points Awarded', field: 'points_awarded' },
];

async function load() {
  try {
    const { data: p } = await api.get('/v1/players/', { params: { page_size: 500 } });
    const pList = p.results || p;
    players.value = pList.map((pl: any) => ({ ...pl, fullName: `${pl.first_name} ${pl.last_name}` }));

    const { data: h } = await api.get('/v1/players/loyalty-points/', { params: { page_size: 500 } });
    pointsHistory.value = h.results || h;

    const { data: r } = await api.get('/v1/players/referral-codes/', { params: { page_size: 200 } });
    const rList = r.results || r;
    referrals.value = rList.map((ref: any) => ({ ...ref, displayCode: `${ref.code} (${ref.user_email || ref.user})` }));
  } catch { /* ignore */ }
}

async function awardPoints() {
  if (!awardForm.value.player || !awardForm.value.reason) {
    $q.notify({ type: 'warning', message: 'Select a player and provide a reason' });
    return;
  }
  awarding.value = true;
  try {
    await api.post('/v1/players/loyalty-points/', {
      player: awardForm.value.player.id,
      points: awardForm.value.points,
      reason: awardForm.value.reason,
    });
    $q.notify({ type: 'positive', message: `${awardForm.value.points} points awarded` });
    awardForm.value = { player: null, points: 10, reason: '' };
    await load();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to award points' });
  } finally {
    awarding.value = false;
  }
}

async function awardReferral() {
  if (!refForm.value.code) {
    $q.notify({ type: 'warning', message: 'Select a referral code' });
    return;
  }
  refAwarding.value = true;
  try {
    await api.post(`/v1/players/referral-codes/${refForm.value.code.id}/award_points/`, {
      points: refForm.value.points,
    });
    $q.notify({ type: 'positive', message: `${refForm.value.points} referral points awarded` });
    await load();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to award' });
  } finally {
    refAwarding.value = false;
  }
}

onMounted(load);
</script>

<style scoped lang="scss">
.dash__head {
  display: flex; align-items: flex-end; justify-content: space-between;
  gap: 16px; margin-bottom: 24px;
}
.sams-card { border-radius: 12px; }
</style>