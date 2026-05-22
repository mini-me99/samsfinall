<template>
  <CrudPage title="Groups" singular="Group" resource="groups" :columns="columns" :fields="fields" />
</template>
<script setup lang="ts">
import CrudPage from 'src/components/CrudPage.vue';
const columns = [
  { name: 'name', label: 'Name', field: 'name', align: 'left' as const, sortable: true },
  { name: 'age_min', label: 'Age min', field: 'age_min' },
  { name: 'age_max', label: 'Age max', field: 'age_max' },
  { name: 'capacity', label: 'Capacity', field: 'capacity' },
];
const fields = [
  { name: 'name', label: 'Name' },
  { name: 'age_min', label: 'Age min', type: 'number' as const },
  { name: 'age_max', label: 'Age max', type: 'number' as const },
  { name: 'capacity', label: 'Capacity', type: 'number' as const },
];
</script>
