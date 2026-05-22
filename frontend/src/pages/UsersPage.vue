<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">User Accounts</div>
      <q-space />
      <q-btn color="primary" icon="add" label="Add user" @click="openCreate" />
    </div>

    <q-table
      :rows="rows"
      :columns="columns"
      row-key="id"
      :loading="loading"
      :pagination="{ rowsPerPage: 20 }"
    >
      <template v-slot:body-cell-actions="props">
        <q-td :props="props" class="q-gutter-xs">
          <q-btn flat dense icon="edit" @click="openEdit(props.row)" />
          <q-btn flat dense icon="delete" color="negative" @click="onDelete(props.row)" />
        </q-td>
      </template>
      <template v-slot:body-cell-is_active="props">
        <q-td :props="props">
          <q-chip :color="props.row.is_active ? 'positive' : 'grey'" text-color="white" dense>
            {{ props.row.is_active ? 'Active' : 'Disabled' }}
          </q-chip>
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="dialog">
      <q-card style="min-width: 420px">
        <q-card-section class="text-h6">{{ editing ? 'Edit user' : 'New user' }}</q-card-section>
        <q-card-section class="q-gutter-sm">
          <q-input v-model="form.email" label="Email" type="email" />
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="form.first_name" label="First name" />
            <q-input class="col" v-model="form.last_name" label="Last name" />
          </div>
          <q-input v-model="form.phone" label="Phone" />
          <q-select
            v-model="form.role"
            :options="roleOptions"
            label="Role"
            emit-value
            map-options
          />
          <q-input
            v-model="form.password"
            :label="editing ? 'New password (leave blank to keep)' : 'Password'"
            type="password"
          />
          <q-toggle v-model="form.is_active" label="Active" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" :label="editing ? 'Save' : 'Create'" :loading="saving" @click="onSave" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';

interface UserRow {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  role: string;
  is_active: boolean;
}

const $q = useQuasar();
const rows = ref<UserRow[]>([]);
const loading = ref(false);
const dialog = ref(false);
const saving = ref(false);
const editing = ref<UserRow | null>(null);
const form = ref({
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  role: 'customer',
  password: '',
  is_active: true,
});

const roleOptions = [
  { label: 'Customer', value: 'customer' },
  { label: 'Coach', value: 'coach' },
  { label: 'Operations', value: 'operations' },
  { label: 'Admin', value: 'admin' },
  { label: 'Super Admin', value: 'super_admin' },
];

const columns = [
  { name: 'email', label: 'Email', field: 'email', align: 'left' as const, sortable: true },
  { name: 'first_name', label: 'First', field: 'first_name', align: 'left' as const },
  { name: 'last_name', label: 'Last', field: 'last_name', align: 'left' as const },
  { name: 'role', label: 'Role', field: 'role', align: 'left' as const, sortable: true },
  { name: 'is_active', label: 'Status', field: 'is_active', align: 'left' as const },
  { name: 'actions', label: '', field: 'id', align: 'right' as const },
];

async function load() {
  loading.value = true;
  try {
    const { data } = await api.get('/v1/accounts/users/');
    rows.value = data.results ?? data;
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to load users' });
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editing.value = null;
  form.value = { email: '', first_name: '', last_name: '', phone: '', role: 'customer', password: '', is_active: true };
  dialog.value = true;
}

function openEdit(row: UserRow) {
  editing.value = row;
  form.value = { ...row, password: '' };
  dialog.value = true;
}

async function onSave() {
  saving.value = true;
  try {
    const payload: Record<string, unknown> = { ...form.value };
    if (editing.value && !payload.password) delete payload.password;
    if (editing.value) {
      await api.patch(`/v1/accounts/users/${editing.value.id}/`, payload);
    } else {
      await api.post('/v1/accounts/users/', payload);
    }
    dialog.value = false;
    await load();
    $q.notify({ type: 'positive', message: 'Saved' });
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: unknown } })?.response?.data;
    $q.notify({ type: 'negative', message: `Save failed: ${JSON.stringify(msg ?? '')}` });
  } finally {
    saving.value = false;
  }
}

async function onDelete(row: UserRow) {
  $q.dialog({
    title: 'Delete user',
    message: `Remove ${row.email}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/v1/accounts/users/${row.id}/`);
      await load();
    } catch {
      $q.notify({ type: 'negative', message: 'Delete failed' });
    }
  });
}

onMounted(load);
</script>
