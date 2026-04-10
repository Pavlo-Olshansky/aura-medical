<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'

const store = useNotificationsStore()
const router = useRouter()
const panelOpen = ref(false)

onMounted(() => {
  store.startPolling()
})

onUnmounted(() => {
  store.stopPolling()
})

function togglePanel() {
  panelOpen.value = !panelOpen.value
}

function closePanelOnOutsideClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.notification-wrapper')) {
    panelOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closePanelOnOutsideClick)
})
onUnmounted(() => {
  document.removeEventListener('click', closePanelOnOutsideClick)
})

function formatTimeLeft(dateStr: string): string {
  const diff = new Date(dateStr).getTime() - Date.now()
  if (diff <= 0) return 'зараз'
  const hours = Math.floor(diff / 3600000)
  const mins = Math.floor((diff % 3600000) / 60000)
  if (hours > 0) return `через ${hours} год ${mins} хв`
  return `через ${mins} хв`
}

function reminderLabel(type: string): string {
  return type === 'hour_before' ? 'За 1 годину' : 'За 1 день'
}

async function handleDismiss(r: { entity_type: string; entity_id: number; reminder_type: string }) {
  await store.dismiss(r)
}

function handleNavigate(route: string) {
  panelOpen.value = false
  router.push(route)
}
</script>

<template>
  <div class="notification-wrapper">
    <button class="bell-btn" @click.stop="togglePanel" :title="`Нагадування (${store.count})`">
      <i class="pi pi-bell" />
      <span v-if="store.count > 0" class="badge">{{ store.count }}</span>
    </button>

    <div v-if="panelOpen" class="notification-panel">
      <div class="panel-header">
        <span class="panel-title">Нагадування</span>
      </div>

      <div v-if="store.reminders.length === 0" class="panel-empty">
        Немає нагадувань
      </div>

      <div v-else class="panel-list">
        <div v-for="r in store.reminders" :key="`${r.entity_type}-${r.entity_id}-${r.reminder_type}`" class="reminder-item">
          <div class="reminder-content" @click="handleNavigate(r.route)">
            <span class="reminder-badge">{{ reminderLabel(r.reminder_type) }}</span>
            <div class="reminder-title">{{ r.title }}</div>
            <div class="reminder-time">{{ formatTimeLeft(r.event_date) }}</div>
          </div>
          <button class="dismiss-btn" @click.stop="handleDismiss(r)" title="Закрити">
            <i class="pi pi-times" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notification-wrapper {
  position: relative;
  display: inline-flex;
}
.bell-btn {
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
  font-size: 1.1rem;
  position: relative;
  transition: color 0.2s, background 0.2s;
}
.bell-btn:hover {
  color: var(--accent);
  background: var(--bg-hover);
}
.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--danger);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 50%;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.notification-panel {
  position: absolute;
  bottom: 100%;
  left: 0;
  width: max(280px, calc(100vw - 2rem));
  max-width: 360px;
  max-height: 400px;
  overflow-y: auto;
  background: var(--bg-card);
  border: 1px solid var(--text-muted);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  margin-bottom: 0.5rem;
}
.panel-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
}
.panel-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}
.panel-empty {
  padding: 1.5rem 1rem;
  text-align: center;
  color: var(--text-faint);
  font-size: 0.875rem;
}
.panel-list {
  padding: 0.25rem 0;
}
.reminder-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
}
.reminder-item:last-child {
  border-bottom: none;
}
.reminder-content {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}
.reminder-content:hover .reminder-title {
  color: var(--accent);
}
.reminder-badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  background: var(--bg-hover);
  color: var(--accent);
  margin-bottom: 0.25rem;
}
.reminder-title {
  font-size: 0.8125rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s;
}
.reminder-time {
  font-size: 0.75rem;
  color: var(--text-faint);
  margin-top: 0.125rem;
}
.dismiss-btn {
  background: none;
  border: none;
  color: var(--text-faint);
  cursor: pointer;
  padding: 0.25rem;
  font-size: 0.75rem;
  flex-shrink: 0;
  border-radius: 2px;
  transition: color 0.15s;
}
.dismiss-btn:hover {
  color: var(--danger);
}
</style>
