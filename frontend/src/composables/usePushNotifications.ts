import { ref, computed } from 'vue'
import { getVapidKey, subscribePush, unsubscribePush } from '@/api/push'

const isSubscribed = ref(false)
const permissionState = ref<NotificationPermission>('default')
let currentEndpoint: string | null = null

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  const arr = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i++) {
    arr[i] = raw.charCodeAt(i)
  }
  return arr
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
    permissionState.value = Notification.permission
    try {
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.getSubscription()
      isSubscribed.value = sub !== null
      currentEndpoint = sub?.endpoint ?? null
    } catch {
      isSubscribed.value = false
    }
  }

  async function subscribe(): Promise<boolean> {
    if (!isSupported.value) return false
    try {
      const permission = await Notification.requestPermission()
      permissionState.value = permission
      if (permission !== 'granted') return false

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
    try {
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.getSubscription()
      if (sub) {
        await unsubscribePush(sub.endpoint)
        await sub.unsubscribe()
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
