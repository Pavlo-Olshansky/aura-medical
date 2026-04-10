<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme'

const { mode, cycleTheme } = useTheme()

const icon = computed(() => ({
  dark: 'pi pi-moon',
  light: 'pi pi-sun',
  system: 'pi pi-desktop',
}[mode.value]))

const label = computed(() => ({
  dark: 'Темна тема',
  light: 'Світла тема',
  system: 'Системна тема',
}[mode.value]))
</script>

<template>
  <button class="theme-toggle" @click="cycleTheme" :title="label" v-tooltip.top="label">
    <i :class="icon" />
  </button>
</template>

<style scoped>
.theme-toggle {
  background: none;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background 0.2s;
  font-size: 1.1rem;
}
.theme-toggle:hover {
  color: var(--accent);
  background: var(--bg-hover);
}
</style>
