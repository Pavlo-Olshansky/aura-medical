<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'

const props = defineProps<{
  status: 'active' | 'completed'
}>()

const label = computed(() => (props.status === 'active' ? 'В процесі' : 'Готово'))
const severity = computed(() => (props.status === 'active' ? 'success' : 'secondary'))
</script>

<template>
  <Tag :value="label" :severity="severity" />
</template>
