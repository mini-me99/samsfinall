<template>
  <CrudPage title="Notifications" singular="Notification" resource="notifications"
    :columns="columns" :fields="fields" :defaults="{ channel: 'in_app', status: 'pending' }" />
</template>
<script setup lang="ts">
import CrudPage from 'src/components/CrudPage.vue';
const columns = [
  { name: 'title', label: 'Title', field: 'title', align: 'left' as const },
  { name: 'channel', label: 'Channel', field: 'channel' },
  { name: 'status', label: 'Status', field: 'status' },
  { name: 'sent_at', label: 'Sent', field: 'sent_at' },
];
const fields = [
  { name: 'title', label: 'Title' },
  { name: 'body', label: 'Body' },
  { name: 'channel', label: 'Channel', type: 'select' as const,
    options: ['in_app','email','sms'].map((v) => ({ label: v, value: v })) },
  { name: 'status', label: 'Status', type: 'select' as const,
    options: ['pending','sent','failed','read'].map((v) => ({ label: v, value: v })) },
];
</script>
