<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="not-found">
    <h1>404</h1>
    <p>Сторінку не знайдено</p>
    <button class="p-button p-component" @click="router.push('/')">
      На головну
    </button>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
  text-align: center;
}

.not-found h1 {
  font-size: 4rem;
  margin: 0;
  color: var(--p-primary-color);
}

.not-found p {
  font-size: 1.25rem;
  color: var(--p-text-muted-color);
}
</style>
