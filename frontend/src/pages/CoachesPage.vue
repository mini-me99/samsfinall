<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h6">Coaches</div>
      <q-space />
      <q-input v-model="search" debounce="300" dense filled placeholder="Search" class="q-mr-sm" style="width: 220px">
        <template #append><q-icon name="search" /></template>
      </q-input>
      <q-btn color="primary" icon="add" label="Add Coach" @click="openDialog()" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
      <template v-slot:body-cell-actions="p">
        <q-td :props="p">
          <q-btn flat dense icon="edit" @click="openDialog(p.row)" />
          <q-btn flat dense icon="delete" color="negative" @click="onDelete(p.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section class="text-h6">{{ editing ? 'Edit' : 'New' }} Coach</q-card-section>
        <q-card-section class="q-gutter-sm">
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="form.first_name" label="First name" filled />
            <q-input class="col" v-model="form.last_name" label="Last name" filled />
          </div>
          <q-input v-model="form.email" label="Email (used as login)" type="email" filled />
          <q-input v-model="form.phone" label="Phone" filled />
          <q-input v-model="form.specialty" label="Specialty" filled />
          <q-input v-model="form.bio" label="Bio" filled type="textarea" autogrow />
          <q-input
            v-model="form.password"
            :label="editing ? 'New password (leave blank to keep)' : 'Password for login'"
            type="password"
            filled
          />
          <div v-if="form.login_email" class="text-caption text-positive">
            Login: {{ form.login_email }}
          </div>
          <q-select v-model="form.status" :options="statusOpts" label="Status" filled emit-value map-options />
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
const apiCrud = crud<any>('coaches');
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
];

const columns = [
  { name: 'first_name', label: 'Name', field: (r: any) => `${r.first_name} ${r.last_name}`, align: 'left' as const, sortable: true },
  { name: 'specialty', label: 'Specialty', field: 'specialty' },
  { name: 'email', label: 'Email', field: 'email' },
  { name: 'phone', label: 'Phone', field: 'phone' },
  { name: 'has_account', label: 'Has Login', field: (r: any) => r.user ? 'Yes' : 'No' },
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
    form.value = { ...row, password: '' };
  } else {
    form.value = { first_name: '', last_name: '', email: '', phone: '', specialty: '', bio: '', password: '', status: 'active' };
  }
  dialog.value = true;
}

async function onSave() {
  saving.value = true;
  try {
    const payload: any = { ...form.value };
    // Don't send empty password on edit
    if (editing.value && !payload.password) delete payload.password;
    if (editing.value) {
      await apiCrud.update(editing.value.id, payload);
      $q.notify({ type: 'positive', message: 'Coach updated' });
    } else {
      const resp = await apiCrud.create(payload);
      const coach = resp as any;
      if (coach.email && payload.password) {
        $q.notify({ type: 'positive', message: `Coach created. Login: ${coach.email}` });
      } else {
        $q.notify({ type: 'positive', message: 'Coach created (no login account)' });
      }
    }
    dialog.value = false;
    await fetch();
  } catch (e: any) {
    const msg = e?.response?.data ? JSON.stringify(e.response.data) : 'Save failed';
    $q.notify({ type: 'negative', message: msg });
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
