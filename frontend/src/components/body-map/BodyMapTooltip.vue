<script setup lang="ts">
defineProps<{
  label: string
  visitCount: number
  treatmentCount: number
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
    <div class="tooltip-stat">{{ visitCount }} візитів</div>
    <div v-if="treatmentCount > 0" class="tooltip-stat treatment">
      {{ treatmentCount }} активних лікувань
    </div>
  </div>
</template>

<style scoped>
.body-map-tooltip {
  position: fixed;
  pointer-events: none;
  background: #1e293b;
  color: #fff;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.4;
  z-index: 1000;
  transform: translate(-50%, -100%) translateY(-8px);
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.tooltip-label {
  font-weight: 600;
  margin-bottom: 0.125rem;
}
.tooltip-stat {
  opacity: 0.85;
}
.tooltip-stat.treatment {
  color: #F59E0B;
}
</style>
