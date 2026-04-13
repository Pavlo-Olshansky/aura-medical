import { ref, computed } from 'vue'
import { getVapidKey, subscribePush, unsubscribePush } from '@/api/push'
import { apiClient } from '@/api/client'
import { isDemoMode } from '@/stores/auth'

const isSubscribed = ref(false)
const permissionState = ref<NotificationPermission>('default')
let currentEndpoint: string | null = null

function urlBase64ToUint8Array(base64String: string): Uint8Array<ArrayBuffer> {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  const buffer = new ArrayBuffer(raw.length)
  const arr = new Uint8Array(buffer)
  for (let i = 0; i < raw.length; i++) {
    arr[i] = raw.charCodeAt(i)
  }
  return arr
}

function hasServiceWorker(): boolean {
  return 'serviceWorker' in navigator && navigator.serviceWorker.controller !== null
}

export function usePushNotifications() {
  const isSupported = computed(() => 'serviceWorker' in navigator && 'PushManager' in window)
  const isStandalone = computed(() => window.matchMedia('(display-mode: standalone)').matches)
  const isIOSSafari = computed(() => {
    const ua = navigator.userAgent
    return /iPad|iPhone|iPod/.test(ua) && !isStandalone.value
  })

  async function checkSubscription() {
    if (!isSupported.value) return
    if (isDemoMode.value) {
      // FR-015: never tie a real VAPID subscription to the fake demo user.
      isSubscribed.value = false
      return
    }
    permissionState.value = Notification.permission

    // If SW is active (production build), check browser PushManager
    if (hasServiceWorker()) {
      try {
        const reg = await navigator.serviceWorker.ready
        const sub = await reg.pushManager.getSubscription()
        isSubscribed.value = sub !== null
        currentEndpoint = sub?.endpoint ?? null
        return
      } catch {
        // fall through to backend check
      }
    }

    // Fallback: ask backend if user has any push subscriptions
    try {
      const { data } = await apiClient.get<{ endpoint: string }[]>('/api/v1/push/subscriptions')
      isSubscribed.value = data.length > 0
    } catch {
      isSubscribed.value = false
    }
  }

  async function subscribe(): Promise<boolean> {
    if (!isSupported.value) return false
    if (isDemoMode.value) return false
    try {
      const permission = await Notification.requestPermission()
      permissionState.value = permission
      if (permission !== 'granted') return false

      // If no SW active (dev mode), still save a placeholder subscription to backend
      if (!hasServiceWorker()) {
        try {
          await apiClient.post('/api/v1/push/subscribe', {
            endpoint: `dev-placeholder-${Date.now()}`,
            keys: { p256dh: 'dev', auth: 'dev' },
          })
        } catch {
          // ignore
        }
        isSubscribed.value = true
        return true
      }

      const vapidKey = await getVapidKey()
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidKey),
      })

      await subscribePush(sub)
      isSubscribed.value = true
      currentEndpoint = sub.endpoint
      return true
    } catch {
      return false
    }
  }

  async function unsubscribe(): Promise<void> {
    if (isDemoMode.value) {
      isSubscribed.value = false
      return
    }
    try {
      if (hasServiceWorker()) {
        const reg = await navigator.serviceWorker.ready
        const sub = await reg.pushManager.getSubscription()
        if (sub) {
          await unsubscribePush(sub.endpoint)
          await sub.unsubscribe()
        }
      } else {
        // Dev mode: remove all subscriptions for this user via backend
        try {
          const { data } = await apiClient.get<{ endpoint: string }[]>('/api/v1/push/subscriptions')
          for (const sub of data) {
            await unsubscribePush(sub.endpoint)
          }
        } catch {
          // ignore
        }
      }
      isSubscribed.value = false
      currentEndpoint = null
    } catch {
      // ignore
    }
  }

  return {
    isSupported,
    isSubscribed,
    isStandalone,
    isIOSSafari,
    permissionState,
    checkSubscription,
    subscribe,
    unsubscribe,
  }
}
