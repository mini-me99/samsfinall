<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h6">Sessions</div>
      <q-space />
      <q-input v-model="fromDate" type="date" filled dense label="From" class="q-mr-sm" />
      <q-input v-model="toDate" type="date" filled dense label="To" class="q-mr-sm" />
      <q-btn color="primary" icon="refresh" label="Load" @click="load" />
    </div>

    <q-table
      :rows="rows"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
    >
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense color="primary" icon="how_to_reg" label="Attendance"
                 @click="openAttendance(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="attDialog" persistent>
      <q-card style="min-width: 520px">
        <q-card-section class="text-h6">Attendance — {{ current?.title }}</q-card-section>
        <q-card-section>
          <q-list bordered separator>
            <q-item v-for="row in attRows" :key="row.player">
              <q-item-section>{{ row.label }}</q-item-section>
              <q-item-section side>
                <q-btn-toggle
                  v-model="row.status"
                  dense
                  :options="[
                    { label: 'P', value: 'present' },
                    { label: 'L', value: 'late' },
                    { label: 'A', value: 'absent' },
                    { label: 'E', value: 'excused' },
                  ]"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :loading="saving" @click="saveAttendance" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import { crud } from 'src/services/crud';

const $q = useQuasar();
const today = new Date();
const in14 = new Date(Date.now() + 14 * 86400000);
const fromDate = ref(today.toISOString().slice(0, 10));
const toDate = ref(in14.toISOString().slice(0, 10));
const rows = ref<any[]>([]);
const loading = ref(false);
const attDialog = ref(false);
const current = ref<any>(null);
const attRows = ref<{ player: string; label: string; status: string }[]>([]);
const saving = ref(false);

const columns = [
  { name: 'starts_at', label: 'Starts', field: (r: any) => new Date(r.starts_at).toLocaleString(), align: 'left' as const },
  { name: 'title', label: 'Title', field: 'title' },
  { name: 'status', label: 'Status', field: 'status' },
  { name: 'capacity', label: 'Capacity', field: 'capacity' },
  { name: 'actions', label: '', field: 'id', align: 'right' as const },
];

async function load() {
  loading.value = true;
  try {
    const { data } = await api.get('/v1/sessions/occurrences/', {
      params: { ordering: 'starts_at', page_size: 100 },
    });
    rows.value = (data.results || []).filter((o: any) => {
      const t = o.starts_at?.slice(0, 10);
      return t >= fromDate.value && t <= toDate.value;
    });
  } finally {
    loading.value = false;
  }
}

async function openAttendance(row: any) {
  current.value = row;
  // load enrollments + existing attendance
  const [enr, att, players] = await Promise.all([
    api.get('/v1/sessions/enrollments/', { params: { occurrence: row.id, page_size: 200 } }),
    api.get('/v1/attendance/', { params: { occurrence: row.id, page_size: 200 } }),
    crud<any>('players').list({ page_size: 500 }),
  ]);
  const byId = new Map(players.results.map((p) => [p.id, `${p.first_name} ${p.last_name}`]));
  const attBy = new Map((att.data.results || []).map((a: any) => [a.player, a.status]));
  attRows.value = (enr.data.results || []).map((e: any) => ({
    player: e.player,
    label: byId.get(e.player) || e.player,
    status: attBy.get(e.player) || 'present',
  }));
  attDialog.value = true;
}

async function saveAttendance() {
  saving.value = true;
  try {
    await api.post('/v1/attendance/bulk_mark/', {
      occurrence: current.value.id,
      items: attRows.value.map((r) => ({ player: r.player, status: r.status })),
    });
    $q.notify({ type: 'positive', message: 'Attendance saved' });
    attDialog.value = false;
  } catch {
    $q.notify({ type: 'negative', message: 'Save failed' });
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>
