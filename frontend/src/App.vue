<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import Toast from 'primevue/toast'

const route = useRoute()
</script>

<template>
  <Toast />
  <RouterView v-if="route.name === 'login'" />
  <AppLayout v-else>
    <RouterView />
  </AppLayout>
</template>
