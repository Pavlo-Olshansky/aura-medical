<script setup lang="ts">
defineProps<{
  label: string
  x: number
  y: number
}>()
</script>

<template>
  <div
    class="body-map-tooltip"
    :style="{ left: x + 'px', top: y + 'px' }"
  >
    <div class="tooltip-label">{{ label }}</div>
  </div>
</template>

<style scoped>
.body-map-tooltip {
  position: fixed;
  pointer-events: none;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #e2e8f0;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(51, 65, 85, 0.5);
  font-size: 0.8125rem;
  line-height: 1.4;
  z-index: 1000;
  transform: translate(-50%, -100%) translateY(-8px);
  white-space: nowrap;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.tooltip-label {
  font-weight: 600;
  color: #fff;
}
</style>
