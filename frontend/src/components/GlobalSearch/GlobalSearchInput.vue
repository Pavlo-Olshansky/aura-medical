<script setup lang="ts">
import InputText from 'primevue/inputtext'

const query = defineModel<string>('query', { required: true })

defineEmits<{
  close: []
}>()
</script>

<template>
  <div class="global-search-header">
    <i class="pi pi-search search-icon" />
    <InputText
      v-model="query"
      class="global-search-input"
      placeholder="Пошук по візитам, лікуванням, аналізам, вакцинаціям..."
      autofocus
    />
    <kbd class="search-kbd" @click="$emit('close')">Esc</kbd>
  </div>
</template>

<style scoped>
.global-search-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1rem;
  width: 100%;
}

.search-icon {
  color: var(--text-muted);
  font-size: 1.2rem;
  flex-shrink: 0;
}

:deep(.global-search-input) {
  flex: 1;
  min-width: 0;
  border: none;
  box-shadow: none;
  font-size: 1rem;
  padding: 0.375rem 0;
  background: transparent;
  color: var(--text-primary);
}

:deep(.global-search-input:focus) {
  box-shadow: none;
  outline: none;
}

.search-kbd {
  font-size: 0.65rem;
  padding: 0.125rem 0.4rem;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  background: var(--bg-hover);
}
</style>
