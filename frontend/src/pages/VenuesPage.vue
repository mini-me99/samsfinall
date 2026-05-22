<template>
  <CrudPage title="Venues" singular="Venue" resource="sessions/venues" :columns="columns" :fields="fields" />
</template>
<script setup lang="ts">
import CrudPage from 'src/components/CrudPage.vue';
const columns = [
  { name: 'name', label: 'Name', field: 'name', align: 'left' as const, sortable: true },
  { name: 'address', label: 'Address', field: 'address' },
  { name: 'capacity', label: 'Capacity', field: 'capacity' },
];
const fields = [
  { name: 'name', label: 'Name' },
  { name: 'address', label: 'Address' },
  { name: 'capacity', label: 'Capacity', type: 'number' as const },
];
</script>
