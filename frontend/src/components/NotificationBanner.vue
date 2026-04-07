<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePushNotifications } from '@/composables/usePushNotifications'

const { isSupported, isSubscribed, isStandalone, isIOSSafari, permissionState, checkSubscription, subscribe } =
  usePushNotifications()

const visible = ref(false)
const loading = ref(false)

const DISMISS_KEY = 'push_banner_dismissed_at'
const DISMISS_DAYS = 7

function isDismissed(): boolean {
  try {
    const val = localStorage.getItem(DISMISS_KEY)
    if (!val) return false
    const dismissed = new Date(val)
    const diff = Date.now() - dismissed.getTime()
    return diff < DISMISS_DAYS * 24 * 60 * 60 * 1000
  } catch {
    return false
  }
}

onMounted(async () => {
  await checkSubscription()
  if (!isSupported.value || isSubscribed.value || isDismissed() || permissionState.value === 'denied') return
  visible.value = true
})

async function handleEnable() {
  loading.value = true
  const ok = await subscribe()
  loading.value = false
  if (ok) visible.value = false
}

function handleLater() {
  try {
    localStorage.setItem(DISMISS_KEY, new Date().toISOString())
  } catch {
    // ignore
  }
  visible.value = false
}
</script>

<template>
  <div v-if="visible" class="notification-banner">
    <template v-if="isIOSSafari">
      <i class="pi pi-mobile" />
      <span>Додайте на головний екран для нагадувань: натисніть <strong>Поділитися</strong> → <strong>На Початковий екран</strong></span>
      <button class="banner-btn secondary" @click="handleLater">Зрозуміло</button>
    </template>
    <template v-else>
      <i class="pi pi-bell" />
      <span>Увімкнути нагадування?</span>
      <div class="banner-actions">
        <button class="banner-btn primary" @click="handleEnable" :disabled="loading">
          {{ loading ? 'Зачекайте...' : 'Увімкнути' }}
        </button>
        <button class="banner-btn secondary" @click="handleLater">Пізніше</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.notification-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: var(--text-primary);
}
.notification-banner i {
  color: var(--accent);
  font-size: 1.25rem;
  flex-shrink: 0;
}
.notification-banner span {
  flex: 1;
}
.banner-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}
.banner-btn {
  border: none;
  border-radius: 4px;
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}
.banner-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.banner-btn.primary {
  background: var(--accent);
  color: #050505;
}
.banner-btn.secondary {
  background: var(--bg-hover);
  color: var(--text-muted);
}
</style>
