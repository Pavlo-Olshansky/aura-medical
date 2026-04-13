// Demo mode lifecycle: activation clears any stale JWT tokens, sets the
// demo flag and seeds the auth store with the demo user. Deactivation
// (called from logout) clears everything and drops the cached dataset.

import { useAuthStore } from '@/stores/auth'
import { setDemoMode, isDemoPersisted } from './useDemoMode'
import { getDemoUser } from './data/user'
import { clearDemoCache } from './cache'

export function activateDemo(): void {
  // FR-002: clear any real session tokens to prevent the axios interceptor
  // from accidentally calling the real backend with leftover credentials.
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')

  setDemoMode(true)

  const auth = useAuthStore()
  auth.user = getDemoUser()
}

export function deactivateDemo(): void {
  setDemoMode(false)
  // Drop in-memory generated data so a subsequent activation re-seeds fresh
  // (also prevents stale mutations from leaking across sessions).
  clearDemoCache()
}

export function restoreDemoIfPersisted(): void {
  // Called once at app boot from main.ts. If the user was previously in
  // demo mode and reloaded the page, restore the flag + user without
  // re-clicking the button (FR-003, US1.4).
  if (!isDemoPersisted()) return
  setDemoMode(true)
  const auth = useAuthStore()
  auth.user = getDemoUser()
}
