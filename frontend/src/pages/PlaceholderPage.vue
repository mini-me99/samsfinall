<template>
  <q-page padding>
    <div class="text-h6">{{ title }}</div>
    <p class="text-grey-7">Module scaffold — implement per master plan.</p>
  </q-page>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { computed } from 'vue';

const route = useRoute();
const { t } = useI18n();
const title = computed(() => (route.meta.title ? t(route.meta.title as string) : ''));
</script>
