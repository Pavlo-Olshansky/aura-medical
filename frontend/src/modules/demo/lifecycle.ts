// Demo mode lifecycle: activation clears any stale JWT tokens, sets the
// demo flag and seeds the auth store with the demo user. Deactivation
// (called from logout) clears everything and drops the cached dataset.

import { useAuthStore } from '@/stores/auth'
import { registerDemoAccessors, unregisterDemoAccessors } from '@/stores/demoRegistry'
import { setDemoMode, isDemoPersisted } from './useDemoMode'
import { getDemoUser, getDemoProfile } from './data/user'
import { getDemoReferences } from './data/references'
import { getDemoVisits } from './data/visits'
import { getDemoTreatments } from './data/treatments'
import { getDemoLabResults, getDemoBiomarkers } from './data/labResults'
import { getDemoMetricTypes, getDemoHealthMetrics } from './data/healthMetrics'
import { getDemoVaccinations } from './data/vaccinations'
import { getDemoCalendarEvents } from './data/calendar'
import { getDemoNotifications } from './data/notifications'
import { getDemoWeatherSummary, getDemoWeatherDetail } from './data/weather'
import { demoCreate, demoUpdate, demoDelete } from './mutations'
import { clearDemoCache } from './cache'

function registerAll(): void {
  registerDemoAccessors({
    getUser: getDemoUser,
    getProfile: getDemoProfile,
    getReferences: getDemoReferences,
    getVisits: getDemoVisits,
    getTreatments: getDemoTreatments,
    getLabResults: getDemoLabResults,
    getBiomarkers: getDemoBiomarkers,
    getMetricTypes: getDemoMetricTypes,
    getHealthMetrics: getDemoHealthMetrics,
    getVaccinations: getDemoVaccinations,
    getCalendarEvents: getDemoCalendarEvents,
    getNotifications: getDemoNotifications,
    getWeatherSummary: getDemoWeatherSummary,
    getWeatherDetail: getDemoWeatherDetail,
    create: demoCreate,
    update: demoUpdate,
    remove: demoDelete,
  })
}

export function activateDemo(): void {
  // FR-002: clear any real session tokens to prevent the axios interceptor
  // from accidentally calling the real backend with leftover credentials.
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')

  registerAll()
  setDemoMode(true)

  const auth = useAuthStore()
  auth.user = getDemoUser()
}

export function deactivateDemo(): void {
  setDemoMode(false)
  unregisterDemoAccessors()
  // Drop in-memory generated data so a subsequent activation re-seeds fresh
  // (also prevents stale mutations from leaking across sessions).
  clearDemoCache()
}

export function restoreDemoIfPersisted(): void {
  // Called once at app boot from main.ts. If the user was previously in
  // demo mode and reloaded the page, restore the flag + user without
  // re-clicking the button (FR-003, US1.4).
  if (!isDemoPersisted()) return
  registerAll()
  setDemoMode(true)
  const auth = useAuthStore()
  auth.user = getDemoUser()
}
