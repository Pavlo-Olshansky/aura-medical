import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { listReminders, dismissReminder, type Reminder, type DismissRequest } from '@/api/notifications'

export const useNotificationsStore = defineStore('notifications', () => {
  const reminders = ref<Reminder[]>([])
  const loading = ref(false)
  const count = computed(() => reminders.value.length)

  let pollTimer: ReturnType<typeof setInterval> | null = null

  async function fetch() {
    try {
      loading.value = true
      const data = await listReminders()
      reminders.value = data.items
    } catch {
      // silently fail - notifications are non-critical
    } finally {
      loading.value = false
    }
  }

  async function dismiss(req: DismissRequest) {
    await dismissReminder(req)
    reminders.value = reminders.value.filter(
      (r) =>
        !(r.entity_type === req.entity_type && r.entity_id === req.entity_id && r.reminder_type === req.reminder_type),
    )
  }

  function startPolling(intervalMs = 5 * 60 * 1000) {
    stopPolling()
    fetch()
    pollTimer = setInterval(fetch, intervalMs)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return { reminders, loading, count, fetch, dismiss, startPolling, stopPolling }
})
