<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import ConfirmDialog from 'primevue/confirmdialog'

function handleKeydown(e: KeyboardEvent) {
  if (e.key !== 'Enter') return
  const acceptBtn = document.querySelector('.p-confirmdialog-accept-button') as HTMLElement | null
  if (acceptBtn) {
    e.preventDefault()
    e.stopPropagation()
    acceptBtn.click()
  }
}

onMounted(() => document.addEventListener('keydown', handleKeydown))
onUnmounted(() => document.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <ConfirmDialog />
</template>
