<template>
  <q-page padding>
    <q-tabs v-model="tab" dense align="left" class="q-mb-md">
      <q-tab name="invoices" label="Invoices" />
      <q-tab name="payments" label="Payments" />
    </q-tabs>
    <CrudPage v-if="tab === 'invoices'"
      title="Invoices" singular="Invoice" resource="payments/invoices"
      :columns="invoiceColumns" :fields="invoiceFields" :defaults="{ status: 'draft', currency: 'EGP' }" />
    <CrudPage v-else
      title="Payments" singular="Payment" resource="payments/payments"
      :columns="paymentColumns" :fields="paymentFields" :defaults="{ method: 'cash', currency: 'EGP' }" />
  </q-page>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import CrudPage from 'src/components/CrudPage.vue';
const tab = ref('invoices');
const invoiceColumns = [
  { name: 'number', label: 'Number', field: 'number', align: 'left' as const },
  { name: 'issue_date', label: 'Issued', field: 'issue_date' },
  { name: 'due_date', label: 'Due', field: 'due_date' },
  { name: 'total', label: 'Total', field: 'total' },
  { name: 'currency', label: 'Cur', field: 'currency' },
  { name: 'status', label: 'Status', field: 'status' },
];
const invoiceFields = [
  { name: 'number', label: 'Number' },
  { name: 'issue_date', label: 'Issue date', type: 'date' as const },
  { name: 'due_date', label: 'Due date', type: 'date' as const },
  { name: 'subtotal', label: 'Subtotal', type: 'number' as const },
  { name: 'tax', label: 'Tax', type: 'number' as const },
  { name: 'total', label: 'Total', type: 'number' as const },
  { name: 'currency', label: 'Currency' },
  { name: 'status', label: 'Status', type: 'select' as const,
    options: ['draft','issued','paid','overdue','cancelled'].map((v) => ({ label: v, value: v })) },
];
const paymentColumns = [
  { name: 'received_at', label: 'Received', field: (r: any) => r.received_at?.slice(0, 16).replace('T', ' '), align: 'left' as const },
  { name: 'amount', label: 'Amount', field: 'amount' },
  { name: 'currency', label: 'Cur', field: 'currency' },
  { name: 'method', label: 'Method', field: 'method' },
  { name: 'reference', label: 'Reference', field: 'reference' },
];
const paymentFields = [
  { name: 'amount', label: 'Amount', type: 'number' as const },
  { name: 'currency', label: 'Currency' },
  { name: 'received_at', label: 'Received at (ISO)' },
  { name: 'method', label: 'Method', type: 'select' as const,
    options: ['cash','card','transfer','online'].map((v) => ({ label: v, value: v })) },
  { name: 'reference', label: 'Reference' },
];
</script>
