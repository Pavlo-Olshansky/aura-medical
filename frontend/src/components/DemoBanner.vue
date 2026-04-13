<script setup lang="ts">
// Yellow dismissible banner shown across the top of the main content area
// whenever demo mode is active and the user has not dismissed it for the
// current session (FR-007, US3.1, US3.2).

defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'dismiss'): void
  (e: 'register'): void
}>()
</script>

<template>
  <div v-if="visible" class="demo-banner">
    <i class="pi pi-exclamation-triangle" />
    <span class="msg">Ви в демо-режимі. Дані не зберігаються.</span>
    <RouterLink to="/login" class="cta" @click="emit('register')">Зареєструватися</RouterLink>
    <button class="close" type="button" aria-label="Закрити" @click="emit('dismiss')">
      <i class="pi pi-times" />
    </button>
  </div>
</template>

<style scoped>
.demo-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #facc15;
  color: #1f2937;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-bottom: 1px solid #ca8a04;
}
.demo-banner .msg {
  flex: 1;
}
.demo-banner .cta {
  color: #1f2937;
  text-decoration: underline;
  font-weight: 600;
  font-size: 0.8125rem;
}
.demo-banner .close {
  background: transparent;
  border: none;
  color: #1f2937;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 2px;
}
.demo-banner .close:hover {
  background: rgba(0, 0, 0, 0.1);
}
</style>
