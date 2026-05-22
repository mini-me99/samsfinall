<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h6">{{ title }}</div>
      <q-space />
      <q-input v-model="search" debounce="300" dense filled placeholder="Search" class="q-mr-sm" style="width: 220px">
        <template #append><q-icon name="search" /></template>
      </q-input>
      <q-btn color="primary" icon="add" :label="`New`" @click="openCreate" />
    </div>

    <q-table
      v-model:pagination="pagination"
      :rows="rows"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
      @request="onRequest"
    >
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense icon="edit" @click="openEdit(props.row)" />
          <q-btn flat dense icon="delete" color="negative" @click="onDelete(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 420px">
        <q-card-section class="text-h6">{{ editing ? 'Edit' : 'New' }} {{ singular }}</q-card-section>
        <q-card-section class="q-gutter-sm">
          <template v-for="f in fields" :key="f.name">
            <q-select
              v-if="f.type === 'select'"
              v-model="form[f.name]"
              :options="f.options || []"
              :label="f.label"
              emit-value
              map-options
              filled
            />
            <q-input
              v-else
              v-model="form[f.name]"
              :label="f.label"
              :type="(f.type as any) || 'text'"
              filled
            />
          </template>
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
import { ref, onMounted, reactive, watch } from 'vue';
import { useQuasar, type QTableProps } from 'quasar';
import { crud } from 'src/services/crud';

interface Field {
  name: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'email' | 'select';
  options?: { label: string; value: unknown }[];
}

const props = defineProps<{
  title: string;
  singular: string;
  resource: string;
  columns: QTableProps['columns'];
  fields: Field[];
  defaults?: Record<string, unknown>;
}>();

const api = crud<Record<string, unknown>>(props.resource);
const $q = useQuasar();
const rows = ref<Record<string, unknown>[]>([]);
const loading = ref(false);
const search = ref('');
const dialog = ref(false);
const editing = ref<Record<string, unknown> | null>(null);
const saving = ref(false);
const form = reactive<Record<string, unknown>>({});

const pagination = ref({ page: 1, rowsPerPage: 25, rowsNumber: 0, sortBy: '', descending: false });

const columns: QTableProps['columns'] = [
  ...(props.columns || []),
  { name: 'actions', label: '', field: 'id', align: 'right' as const },
];

async function fetch() {
  loading.value = true;
  try {
    const params: Record<string, unknown> = {
      page: pagination.value.page,
      page_size: pagination.value.rowsPerPage,
    };
    if (search.value) params.search = search.value;
    if (pagination.value.sortBy) {
      params.ordering = (pagination.value.descending ? '-' : '') + pagination.value.sortBy;
    }
    const data = await api.list(params);
    rows.value = data.results;
    pagination.value.rowsNumber = data.count;
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Failed to load' });
  } finally {
    loading.value = false;
  }
}

function onRequest(p: { pagination: typeof pagination.value }) {
  pagination.value = p.pagination;
  void fetch();
}

function openCreate() {
  editing.value = null;
  Object.keys(form).forEach((k) => delete form[k]);
  Object.assign(form, props.defaults || {});
  dialog.value = true;
}

function openEdit(row: Record<string, unknown>) {
  editing.value = row;
  Object.keys(form).forEach((k) => delete form[k]);
  Object.assign(form, row);
  dialog.value = true;
}

async function onSave() {
  saving.value = true;
  try {
    if (editing.value) await api.update(editing.value.id as string, form);
    else await api.create(form);
    dialog.value = false;
    $q.notify({ type: 'positive', message: 'Saved' });
    await fetch();
  } catch {
    $q.notify({ type: 'negative', message: 'Save failed' });
  } finally {
    saving.value = false;
  }
}

async function onDelete(row: Record<string, unknown>) {
  $q.dialog({
    title: 'Delete',
    message: 'Are you sure?',
    cancel: true,
    ok: { label: 'Delete', color: 'negative' },
  }).onOk(async () => {
    await api.remove(row.id as string);
    await fetch();
  });
}

onMounted(fetch);

watch(search, () => { pagination.value.page = 1; void fetch(); });
</script>
