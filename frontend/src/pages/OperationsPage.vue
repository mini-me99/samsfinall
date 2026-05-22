<template>
  <q-page class="sams-page">
    <header class="dash__head">
      <div>
        <div class="sams-eyebrow">Operations</div>
        <h1 class="sams-title">Operations Dashboard</h1>
        <p class="sams-subtitle">Add customers with preferences, link them to coaches, and link partners together.</p>
      </div>
      <q-btn color="primary" icon="refresh" label="Refresh" @click="loadAll" />
    </header>

    <q-tabs v-model="tab" dense align="left" class="q-mb-md">
      <q-tab name="customers" label="Customers" />
      <q-tab name="add" label="Add Customer" />
      <q-tab name="linkCoach" label="Link to Coach" />
      <q-tab name="linkPartners" label="Link Partners" />
      <q-tab name="dues" label="Dues & Payments" />
    </q-tabs>

    <!-- Customers Tab -->
    <section v-if="tab === 'customers'">
      <q-card class="sams-card q-mb-md" flat bordered>
        <q-card-section class="row items-center">
          <div class="text-h6 col">All Customers ({{ customers.length }})</div>
          <q-input v-model="customerSearch" debounce="300" dense filled placeholder="Search by name, phone, email..." class="col-4">
            <template #append><q-icon name="search" /></template>
          </q-input>
        </q-card-section>
      </q-card>
      <q-table
        :rows="filteredCustomers"
        :columns="customerCols"
        row-key="id"
        flat
        bordered
        :loading="loading"
      >
        <template v-slot:body-cell-actions="p">
          <q-td :props="p">
            <q-btn flat dense icon="edit" size="sm" @click="openEditDialog(p.row)" />
          </q-td>
        </template>
      </q-table>
    </section>

    <!-- Add Customer Tab -->
    <section v-if="tab === 'add'">
      <q-card class="sams-card" flat bordered>
        <q-card-section class="text-h6">{{ editingCustomer ? 'Edit' : 'Add New' }} Customer</q-card-section>
        <q-card-section class="q-gutter-md">
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="custForm.first_name" label="First name *" filled :rules="[v => !!v || 'Required']" />
            <q-input class="col" v-model="custForm.last_name" label="Last name *" filled :rules="[v => !!v || 'Required']" />
          </div>
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="custForm.email" label="Email" type="email" filled />
            <q-input class="col" v-model="custForm.phone" label="Phone" filled />
          </div>
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="custForm.date_of_birth" label="Date of birth" type="date" filled />
            <q-select class="col" v-model="custForm.status" :options="statusOpts" label="Status" filled emit-value map-options />
          </div>

          <q-separator />
          <div class="text-subtitle2 text-weight-bold">Session Preferences</div>
          <q-select v-model="custForm.preference_type" :options="prefOpts" label="Preference" filled emit-value map-options />
          <q-select v-model="custForm.preferred_days" :options="dayOpts" label="Preferred days" multiple filled use-chips />
          <q-input v-model="custForm.preferred_time" label="Preferred time" type="time" filled />

          <q-separator />
          <div class="text-subtitle2 text-weight-bold">Link to Existing User Account</div>
          <q-select
            v-model="custForm.user_id"
            :options="userSearchResults"
            option-value="id"
            option-label="email"
            label="Search existing user account..."
            filled
            clearable
            use-input
            input-debounce="300"
            @filter="filterUserAccounts"
          >
            <template v-slot:no-option>
              <q-item><q-item-section class="text-grey">Type to search users</q-item-section></q-item>
            </template>
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.email }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.first_name }} {{ scope.opt.last_name }} ({{ scope.opt.role }})</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
          <div class="text-caption text-grey">Or create a new account automatically:</div>
          <q-input v-model="custForm.password" label="Password (for auto-created account)" type="password" filled :disable="!!custForm.user_id" />

          <q-separator />
          <div class="text-subtitle2 text-weight-bold">Link to Coach</div>
          <q-select
            v-model="custForm.linkCoach"
            :options="coachOptions"
            option-value="id"
            option-label="fullName"
            label="Assign to coach (optional)"
            filled
            clearable
            use-input
            input-debounce="300"
            @filter="filterCoaches"
          >
            <template v-slot:no-option>
              <q-item><q-item-section class="text-grey">Type to search coaches</q-item-section></q-item>
            </template>
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.fullName }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.specialty }} — {{ scope.opt.email }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Clear" @click="resetForm" />
          <q-btn color="primary" label="Save Customer" :loading="saving" @click="saveCustomer" />
        </q-card-actions>
      </q-card>
    </section>

    <!-- Link to Coach Tab -->
    <section v-if="tab === 'linkCoach'">
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Assign Customer to Coach</q-card-section>
            <q-card-section class="q-gutter-sm">
              <q-select
                v-model="linkForm.player"
                :options="filteredCustomers"
                option-value="id"
                option-label="fullName"
                label="Search customer..."
                filled
                use-input
                input-debounce="300"
                @filter="filterPlayers"
              >
                <template v-slot:no-option>
                  <q-item><q-item-section class="text-grey">Type to search</q-item-section></q-item>
                </template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label>{{ scope.opt.fullName }}</q-item-label>
                      <q-item-label caption>{{ scope.opt.phone }} | {{ scope.opt.preference_type }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
              <q-select
                v-model="linkForm.coach"
                :options="coachOptions"
                option-value="id"
                option-label="fullName"
                label="Search coach..."
                filled
                use-input
                input-debounce="300"
                @filter="filterCoaches"
              >
                <template v-slot:no-option>
                  <q-item><q-item-section class="text-grey">Type to search</q-item-section></q-item>
                </template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label>{{ scope.opt.fullName }}</q-item-label>
                      <q-item-label caption>{{ scope.opt.specialty }} | {{ scope.opt.email }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn color="primary" label="Link Now" :loading="linking" @click="linkToCoach" />
            </q-card-actions>
          </q-card>
        </div>
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Current Coach Links ({{ coachLinks.length }})</q-card-section>
            <q-table :rows="coachLinks" :columns="linkCols" row-key="id" flat bordered hide-pagination />
          </q-card>
        </div>
      </div>
    </section>

    <!-- Link Partners Tab -->
    <section v-if="tab === 'linkPartners'">
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Link Two Customers as Partners</q-card-section>
            <q-card-section class="q-gutter-sm">
              <q-select
                v-model="partnerForm.player1"
                :options="filteredCustomers"
                option-value="id"
                option-label="fullName"
                label="First customer..."
                filled
                use-input
                input-debounce="300"
                @filter="filterPlayers"
              >
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label>{{ scope.opt.fullName }}</q-item-label>
                      <q-item-label caption>{{ scope.opt.phone }} | {{ scope.opt.email }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
              <q-select
                v-model="partnerForm.player2"
                :options="filteredCustomers"
                option-value="id"
                option-label="fullName"
                label="Second customer..."
                filled
                use-input
                input-debounce="300"
                @filter="filterPlayers"
              >
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label>{{ scope.opt.fullName }}</q-item-label>
                      <q-item-label caption>{{ scope.opt.phone }} | {{ scope.opt.email }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn color="primary" label="Link as Partners" :loading="partnering" @click="linkPartners" />
            </q-card-actions>
          </q-card>
        </div>
        <div class="col-12 col-md-6">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Current Partner Links ({{ partneredCustomers.length }})</q-card-section>
            <q-list bordered separator>
              <q-item v-for="p in partneredCustomers" :key="p.id">
                <q-item-section>{{ p.first_name }} {{ p.last_name }}</q-item-section>
                <q-item-section side>
                  <q-chip color="primary" dense>Partner: {{ p.partnerName }}</q-chip>
                </q-item-section>
              </q-item>
              <q-item v-if="partneredCustomers.length === 0">
                <q-item-section class="text-grey text-center">No partners linked yet</q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Edit Customer Dialog -->
    <q-dialog v-model="editDialog" persistent>
      <q-card style="min-width: 550px">
        <q-card-section class="text-h6">Edit Customer</q-card-section>
        <q-card-section class="q-gutter-sm">
          <div class="row q-col-gutter-sm">
            <q-input class="col" v-model="editForm.first_name" label="First name" filled />
            <q-input class="col" v-model="editForm.last_name" label="Last name" filled />
          </div>
          <q-input v-model="editForm.email" label="Email" filled />
          <q-input v-model="editForm.phone" label="Phone" filled />
          <q-select v-model="editForm.status" :options="statusOpts" label="Status" filled emit-value map-options />
          <q-select v-model="editForm.preference_type" :options="prefOpts" label="Preference" filled emit-value map-options />
          <q-select v-model="editForm.preferred_days" :options="dayOpts" label="Days" multiple filled use-chips />
          <q-input v-model="editForm.preferred_time" label="Time" type="time" filled />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :loading="saving" @click="saveEdit" />
        </q-card-actions>
      </q-card>
    <!-- Dues Tab -->
    <section v-if="tab === 'dues'">
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-5">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Add Due Amount</q-card-section>
            <q-card-section class="q-gutter-sm">
              <q-select v-model="dueForm.player" :options="customerOptions" option-value="id" option-label="fullName" label="Select customer" filled use-input input-debounce="300" @filter="filterDuesPlayers" />
              <q-input v-model="dueForm.amount" type="number" label="Amount (EGP)" filled :min="1" />
              <q-input v-model="dueForm.description" label="Description (e.g. Monthly fee)" filled />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn color="primary" label="Add Due" :loading="savingDue" @click="addDue" />
            </q-card-actions>
          </q-card>
          <q-card class="sams-card q-mt-md" flat bordered>
            <q-card-section class="text-h6">Mark as Paid</q-card-section>
            <q-card-section class="q-gutter-sm">
              <q-select v-model="payForm.invoice" :options="unpaidInvoices" option-value="id" option-label="displayLabel" label="Select unpaid invoice" filled />
              <q-input v-model="payForm.amount" type="number" label="Amount paid" filled />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn color="positive" label="Mark Paid" :loading="savingPay" @click="markPaid" />
            </q-card-actions>
          </q-card>
        </div>
        <div class="col-12 col-md-7">
          <q-card class="sams-card" flat bordered>
            <q-card-section class="text-h6">Payment History</q-card-section>
            <q-table :rows="paymentHistory" :columns="paymentCols" row-key="id" flat bordered hide-pagination />
          </q-card>
        </div>
      </div>
    </section>

    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';

const $q = useQuasar();
const tab = ref('customers');
const loading = ref(false);
const saving = ref(false);
const linking = ref(false);
const partnering = ref(false);
const editDialog = ref(false);
const editingCustomer = ref<any>(null);
const customerSearch = ref('');

const customers = ref<any[]>([]);
const coachList = ref<any[]>([]);
const coachLinks = ref<any[]>([]);
const allUserAccounts = ref<any[]>([]);
const userSearchResults = ref<any[]>([]);
const coachSearchResults = ref<any[]>([]);

// Dues state
const savingDue = ref(false);
const savingPay = ref(false);
const duesList = ref<any[]>([]);
const paymentHistory = ref<any[]>([]);
const dueForm = ref({ player: null as any, amount: 100, description: '' });
const payForm = ref({ invoice: null as any, amount: 0 });

const unpaidInvoices = computed(() =>
  duesList.value
    .filter((i: any) => i.status !== 'paid')
    .map((i: any) => ({ ...i, displayLabel: `${i.player_name || i.player} — ${i.total} EGP (${i.status})` }))
);

const paymentCols = [
  { name: 'player', label: 'Player', field: (r: any) => r.player_name || r.player, align: 'left' as const },
  { name: 'total', label: 'Amount', field: 'total' },
  { name: 'status', label: 'Status', field: 'status' },
  { name: 'issue_date', label: 'Date', field: 'issue_date' },
];

function filterDuesPlayers(val: string, update: (fn: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    customerOptions.value = customers.value
      .filter((c: any) => !needle || (c.first_name + ' ' + c.last_name + ' ' + (c.phone || '')).toLowerCase().includes(needle))
      .slice(0, 50);
  });
}

async function addDue() {
  if (!dueForm.value.player || !dueForm.value.amount) {
    $q.notify({ type: 'warning', message: 'Select a player and enter amount' });
    return;
  }
  savingDue.value = true;
  try {
    const today = new Date().toISOString().slice(0, 10);
    const in30 = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);
    await api.post('/v1/payments/invoices/', {
      player: dueForm.value.player.id,
      total: dueForm.value.amount,
      subtotal: dueForm.value.amount,
      issue_date: today,
      due_date: in30,
      status: 'issued',
      number: `DUE-${Date.now()}`,
    });
    $q.notify({ type: 'positive', message: `Due added: ${dueForm.value.amount} EGP` });
    dueForm.value = { player: null, amount: 100, description: '' };
    await loadDues();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to add due' });
  } finally {
    savingDue.value = false;
  }
}

async function markPaid() {
  if (!payForm.value.invoice) {
    $q.notify({ type: 'warning', message: 'Select an invoice' });
    return;
  }
  savingPay.value = true;
  try {
    const inv = payForm.value.invoice;
    const amount = payForm.value.amount || inv.total;
    await api.post('/v1/payments/payments/', {
      invoice: inv.id,
      player: inv.player,
      amount: amount,
      received_at: new Date().toISOString(),
      method: 'cash',
    });
    await api.patch(`/v1/payments/invoices/${inv.id}/`, { status: 'paid' });
    $q.notify({ type: 'positive', message: `Payment of ${amount} EGP recorded` });
    payForm.value = { invoice: null, amount: 0 };
    await loadDues();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to record payment' });
  } finally {
    savingPay.value = false;
  }
}

async function loadDues() {
  try {
    const [invResp, payResp] = await Promise.all([
      api.get('/v1/payments/invoices/', { params: { page_size: 500 } }).catch(() => ({ data: { results: [] } })),
      api.get('/v1/payments/payments/', { params: { page_size: 500 } }).catch(() => ({ data: { results: [] } })),
    ]);
    duesList.value = (invResp.data.results || invResp.data).map((i: any) => {
      const player = customers.value.find((p: any) => p.id === i.player);
      return { ...i, player_name: player ? `${player.first_name} ${player.last_name}` : i.player };
    });
    paymentHistory.value = (payResp.data.results || payResp.data).map((p: any) => {
      const player = customers.value.find((c: any) => c.id === p.player);
      return { ...p, player_name: player ? `${player.first_name} ${player.last_name}` : p.player };
    });
  } catch { /* ignore */ }
}

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

const custForm = ref({
  first_name: '', last_name: '', email: '', phone: '', date_of_birth: '',
  status: 'active', preference_type: 'alone', preferred_days: [] as string[],
  preferred_time: '', user_id: null as any, password: '', linkCoach: null as any,
});
const editForm = ref<any>({});
const linkForm = ref({ player: null as any, coach: null as any });
const partnerForm = ref({ player1: null as any, player2: null as any });

const filteredCustomers = computed(() => {
  const q = customerSearch.value.toLowerCase().trim();
  if (!q) return customers.value;
  return customers.value.filter((c: any) =>
    (c.first_name + ' ' + c.last_name).toLowerCase().includes(q) ||
    (c.phone || '').includes(q) ||
    (c.email || '').toLowerCase().includes(q)
  );
});

const coachOptions = computed(() =>
  coachList.value.map((c: any) => ({ ...c, fullName: `${c.first_name} ${c.last_name}` }))
);

const partneredCustomers = computed(() =>
  customers.value.filter((c: any) => {
    const partner = c.linked_partner ? customers.value.find((p: any) => p.id === c.linked_partner) : null;
    if (partner) c.partnerName = `${partner.first_name} ${partner.last_name}`;
    return c.linked_partner;
  })
);

const customerCols = [
  { name: 'name', label: 'Name', field: (r: any) => `${r.first_name} ${r.last_name}`, align: 'left' as const },
  { name: 'phone', label: 'Phone', field: 'phone' },
  { name: 'email', label: 'Email', field: 'email' },
  { name: 'preference_type', label: 'Pref', field: 'preference_type' },
  { name: 'preferred_days', label: 'Days', field: (r: any) => (r.preferred_days || []).join(', ') },
  { name: 'preferred_time', label: 'Time', field: 'preferred_time' },
  { name: 'has_partner', label: 'Partner', field: (r: any) => r.linked_partner_name || '—' },
  { name: 'status', label: 'Status', field: 'status' },
  { name: 'actions', label: '', field: 'id', align: 'right' as const },
];

const linkCols = [
  { name: 'player', label: 'Customer', field: (r: any) => r.player_name || r.player, align: 'left' as const },
  { name: 'coach', label: 'Coach', field: (r: any) => r.coach_name || r.coach },
];

function filterPlayers(val: string, update: (fn: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    customerOptions.value = customers.value
      .filter((c: any) => !needle || (c.first_name + ' ' + c.last_name + ' ' + (c.phone || '') + ' ' + (c.email || '')).toLowerCase().includes(needle))
      .slice(0, 50);
  });
}
const customerOptions = ref<any[]>([]);

function filterCoaches(val: string, update: (fn: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    coachSearchResults.value = coachList.value
      .filter((c: any) => !needle || (c.first_name + ' ' + c.last_name + ' ' + (c.email || '') + ' ' + (c.specialty || '')).toLowerCase().includes(needle))
      .map((c: any) => ({ ...c, fullName: `${c.first_name} ${c.last_name}` }));
  });
}

function filterUserAccounts(val: string, update: (fn: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    userSearchResults.value = allUserAccounts.value
      .filter((u: any) => !needle || (u.email + ' ' + (u.first_name || '') + ' ' + (u.last_name || '')).toLowerCase().includes(needle))
      .slice(0, 50);
  });
}

async function loadAll() {
  loading.value = true;
  const errors: string[] = [];
  try {
    const [pResp, cResp, lResp, uResp] = await Promise.all([
      api.get('/v1/players/', { params: { page_size: 500 } }).catch((e) => { errors.push('players'); return { data: { results: [] } }; }),
      api.get('/v1/coaches/', { params: { page_size: 200 } }).catch((e) => { errors.push('coaches'); return { data: { results: [] } }; }),
      api.get('/v1/players/coach-links/', { params: { page_size: 500 } }).catch((e) => { errors.push('coach-links'); return { data: { results: [] } }; }),
      api.get('/v1/accounts/users/search/', { params: { page_size: 500 } }).catch((e) => { errors.push('users'); return { data: { results: [] } }; }),
    ]);
    customers.value = (pResp.data.results || pResp.data).map((c: any) => {
      if (c.linked_partner) {
        const partner = (pResp.data.results || pResp.data).find((p: any) => p.id === c.linked_partner);
        c.linked_partner_name = partner ? `${partner.first_name} ${partner.last_name}` : '—';
      }
      return { ...c, fullName: `${c.first_name} ${c.last_name}` };
    });
    customerOptions.value = customers.value.slice(0, 50);
    coachList.value = (cResp.data.results || cResp.data);
    coachLinks.value = (lResp.data.results || lResp.data).map((l: any) => {
      const coach = coachList.value.find((c: any) => c.id === l.coach);
      const player = customers.value.find((p: any) => p.id === l.player);
      return { ...l, coach_name: coach ? `${coach.first_name} ${coach.last_name}` : l.coach, player_name: player ? `${player.first_name} ${player.last_name}` : l.player };
    });
    allUserAccounts.value = (uResp.data.results || uResp.data);
    userSearchResults.value = allUserAccounts.value.slice(0, 50);
    await loadDues();
  } catch (e) {
    errors.push('general');
  } finally {
    loading.value = false;
    if (errors.length > 0) {
      $q.notify({ type: 'warning', message: `Some data failed to load: ${errors.join(', ')}. Check permissions.` });
    }
  }
}

function resetForm() {
  custForm.value = {
    first_name: '', last_name: '', email: '', phone: '', date_of_birth: '',
    status: 'active', preference_type: 'alone', preferred_days: [],
    preferred_time: '', user_id: null, password: '', linkCoach: null,
  };
}

function openEditDialog(row: any) {
  editingCustomer.value = row;
  editForm.value = {
    first_name: row.first_name, last_name: row.last_name, email: row.email, phone: row.phone,
    status: row.status, preference_type: row.preference_type,
    preferred_days: row.preferred_days || [], preferred_time: row.preferred_time || '',
    date_of_birth: row.date_of_birth || '',
  };
  editDialog.value = true;
}

async function saveCustomer() {
  if (!custForm.value.first_name || !custForm.value.last_name) {
    $q.notify({ type: 'warning', message: 'First name and last name are required' });
    return;
  }
  saving.value = true;
  try {
    const payload: any = {
      first_name: custForm.value.first_name,
      last_name: custForm.value.last_name,
      email: custForm.value.email || '',
      phone: custForm.value.phone || '',
      date_of_birth: custForm.value.date_of_birth || null,
      status: custForm.value.status,
      preference_type: custForm.value.preference_type,
      preferred_days: custForm.value.preferred_days,
      preferred_time: custForm.value.preferred_time || null,
      user: custForm.value.user_id?.id || custForm.value.user_id || null,
    };
    // Backend handles account creation when password is sent
    if (custForm.value.password && !custForm.value.user_id) {
      payload.password = custForm.value.password;
    }
    const playerResp = await api.post('/v1/players/', payload);
    const playerId = playerResp.data.id;

    // Link to coach if selected
    if (custForm.value.linkCoach) {
      try {
        await api.post('/v1/players/coach-links/', {
          player: playerId,
          coach: custForm.value.linkCoach.id,
        });
      } catch { /* ignore link errors */ }
    }

    const hasAcct = playerResp.data.user ? ' with login account' : '';
    $q.notify({ type: 'positive', message: `Customer ${custForm.value.first_name} ${custForm.value.last_name} added${hasAcct}` });
    resetForm();
    await loadAll();
  } catch (e: any) {
    const msg = e.response?.data ? JSON.stringify(e.response.data) : 'Save failed';
    $q.notify({ type: 'negative', message: msg });
  } finally {
    saving.value = false;
  }
}

async function saveEdit() {
  saving.value = true;
  try {
    await api.patch(`/v1/players/${editingCustomer.value.id}/`, editForm.value);
    $q.notify({ type: 'positive', message: 'Customer updated' });
    editDialog.value = false;
    await loadAll();
  } catch {
    $q.notify({ type: 'negative', message: 'Update failed' });
  } finally {
    saving.value = false;
  }
}

async function linkToCoach() {
  if (!linkForm.value.player || !linkForm.value.coach) {
    $q.notify({ type: 'warning', message: 'Select both a customer and a coach' });
    return;
  }
  linking.value = true;
  try {
    await api.post('/v1/players/coach-links/', {
      player: linkForm.value.player.id,
      coach: linkForm.value.coach.id,
    });
    $q.notify({ type: 'positive', message: `${linkForm.value.player.first_name} linked to ${linkForm.value.coach.first_name}` });
    linkForm.value = { player: null, coach: null };
    await loadAll();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to link' });
  } finally {
    linking.value = false;
  }
}

async function linkPartners() {
  if (!partnerForm.value.player1 || !partnerForm.value.player2) {
    $q.notify({ type: 'warning', message: 'Select two customers' });
    return;
  }
  partnering.value = true;
  try {
    const p1 = partnerForm.value.player1;
    const p2 = partnerForm.value.player2;
    await api.patch(`/v1/players/${p1.id}/`, { linked_partner: p2.id, preference_type: 'partner' });
    await api.patch(`/v1/players/${p2.id}/`, { linked_partner: p1.id, preference_type: 'partner' });
    $q.notify({ type: 'positive', message: `${p1.first_name} and ${p2.first_name} are now partners` });
    partnerForm.value = { player1: null, player2: null };
    await loadAll();
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to link partners' });
  } finally {
    partnering.value = false;
  }
}

onMounted(loadAll);
</script>

<style scoped lang="scss">
.dash__head {
  display: flex; align-items: flex-end; justify-content: space-between;
  gap: 16px; margin-bottom: 24px;
}
.sams-card { border-radius: 12px; }
</style>