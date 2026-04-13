// Composable for demo-mode reactive state (FR-001).
// The underlying `isDemoMode` ref is owned by `@/stores/auth` so every
// Pinia store can check the flag without dynamic-importing this lazy
// module (research.md R3). This file mutates that ref via setDemoMode().

import { ref, readonly } from 'vue'
import { isDemoMode } from '@/stores/auth'

export const DEMO_STORAGE_KEY = 'medtracker_demo_mode'

const _bannerVisible = ref(true)

export { isDemoMode }

export function useDemoMode() {
  return {
    isDemoMode: readonly(isDemoMode),
    bannerVisible: readonly(_bannerVisible),
    setDemoMode,
    dismissBanner,
  }
}

export function setDemoMode(value: boolean): void {
  isDemoMode.value = value
  if (value) {
    localStorage.setItem(DEMO_STORAGE_KEY, 'true')
    // Re-show banner on every fresh activation (US3.2 dismissal is
    // session-only; reload restores it per research.md R4).
    _bannerVisible.value = true
  } else {
    localStorage.removeItem(DEMO_STORAGE_KEY)
  }
}

export function dismissBanner(): void {
  _bannerVisible.value = false
}

export function isDemoPersisted(): boolean {
  return localStorage.getItem(DEMO_STORAGE_KEY) === 'true'
}
