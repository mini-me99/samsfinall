<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h6">Players</div>
      <q-space />
      <q-input v-model="search" debounce="300" dense filled placeholder="Search" class="q-mr-sm" style="width: 220px">
        <template #append><q-icon name="search" /></template>
      </q-input>
      <q-btn color="primary" icon="add" label="Add Player" @click="openDialog()" />
    </div>

    <q-table
      :rows="rows"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
    >
      <template v-slot:body-cell-actions="p">
        <q-td :props="p">
          <q-btn flat dense icon="edit" @click="openDialog(p.row)" />
          <q-btn flat dense icon="delete" color="negative" @click="onDelete(p.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section class="text-h6">{{ editing ? 'Edit' : 'New' }} Player</q-card-section>
        <q-card-section class="q-gutter-sm">
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="form.first_name" label="First name" filled />
            <q-input class="col" v-model="form.last_name" label="Last name" filled />
          </div>
          <q-input v-model="form.email" label="Email" type="email" filled />
          <q-input v-model="form.phone" label="Phone" filled />
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="form.date_of_birth" label="Date of birth" type="date" filled />
            <q-select class="col" v-model="form.status" :options="statusOpts" label="Status" filled emit-value map-options />
          </div>

          <q-separator />
          <div class="text-subtitle2 text-weight-bold">Session Preferences</div>
          <q-select v-model="form.preference_type" :options="prefOpts" label="Preference (Alone / Partner / Group)" filled emit-value map-options />
          <q-select v-model="form.preferred_days" :options="dayOpts" label="Preferred days" multiple filled use-chips />
          <q-input v-model="form.preferred_time" label="Preferred time" type="time" filled />

          <q-separator />
          <div class="text-subtitle2 text-weight-bold">Guardian Info</div>
          <q-input v-model="form.guardian_name" label="Guardian name" filled />
          <q-input v-model="form.guardian_phone" label="Guardian phone" filled />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :loading="saving" @click="onSave" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import { crud } from 'src/services/crud';

const $q = useQuasar();
const apiCrud = crud<any>('players');
const rows = ref<any[]>([]);
const loading = ref(false);
const search = ref('');
const dialog = ref(false);
const editing = ref<any>(null);
const saving = ref(false);
const form = ref<any>({});

const statusOpts = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Archived', value: 'archived' },
];
const prefOpts = [
  { label: 'Alone', value: 'alone' },
  { label: 'With Partner', value: 'partner' },
  { label: 'In a Group', value: 'group' },
];
const dayOpts = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];

const columns = [
  { name: 'first_name', label: 'Name', field: (r: any) => `${r.first_name} ${r.last_name}`, align: 'left' as const, sortable: true },
  { name: 'preference_type', label: 'Preference', field: 'preference_type' },
  { name: 'preferred_days', label: 'Days', field: (r: any) => (r.preferred_days || []).join(', ') },
  { name: 'preferred_time', label: 'Time', field: 'preferred_time' },
  { name: 'phone', label: 'Phone', field: 'phone' },
  { name: 'status', label: 'Status', field: 'status' },
  { name: 'actions', label: '', field: 'id', align: 'right' as const },
];

async function fetch() {
  loading.value = true;
  try {
    const params: any = { page_size: 500 };
    if (search.value) params.search = search.value;
    const data = await apiCrud.list(params);
    rows.value = data.results || data;
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to load' });
  } finally {
    loading.value = false;
  }
}

function openDialog(row?: any) {
  editing.value = row || null;
  if (row) {
    form.value = { ...row, preferred_days: row.preferred_days || [] };
  } else {
    form.value = { first_name: '', last_name: '', email: '', phone: '', date_of_birth: '', status: 'active', preference_type: 'alone', preferred_days: [], preferred_time: '', guardian_name: '', guardian_phone: '' };
  }
  dialog.value = true;
}

async function onSave() {
  saving.value = true;
  try {
    const payload = { ...form.value };
    if (editing.value) {
      await apiCrud.update(editing.value.id, payload);
    } else {
      await apiCrud.create(payload);
    }
    dialog.value = false;
    $q.notify({ type: 'positive', message: 'Saved' });
    await fetch();
  } catch {
    $q.notify({ type: 'negative', message: 'Save failed' });
  } finally {
    saving.value = false;
  }
}

async function onDelete(row: any) {
  $q.dialog({
    title: 'Delete',
    message: 'Are you sure?',
    cancel: true,
    ok: { label: 'Delete', color: 'negative' },
  }).onOk(async () => {
    await apiCrud.remove(row.id);
    await fetch();
  });
}

onMounted(fetch);
watch(search, () => fetch());
</script>
