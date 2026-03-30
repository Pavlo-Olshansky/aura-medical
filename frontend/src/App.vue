<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
</script>

<template>
  <RouterView v-if="route.name === 'login'" />
  <AppLayout v-else>
    <RouterView />
  </AppLayout>
</template>
