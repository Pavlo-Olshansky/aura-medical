// Public API of the lazy-loaded demo module.
// This file is the only entry point that other parts of the app may import.
// The full module body is implemented across foundational tasks (T005-T015)
// and per-user-story tasks. This file's exports stay stable per
// contracts/demo-module.md.

export { useDemoMode, isDemoMode } from './useDemoMode'
export { activateDemo, deactivateDemo, restoreDemoIfPersisted } from './lifecycle'
export { demoCreate, demoUpdate, demoDelete } from './mutations'

export { getDemoUser, getDemoProfile } from './data/user'
export { getDemoReferences } from './data/references'
export { getDemoVisits } from './data/visits'
export { getDemoTreatments } from './data/treatments'
export { getDemoLabResults, getDemoBiomarkers } from './data/labResults'
export { getDemoHealthMetrics, getDemoMetricTypes } from './data/healthMetrics'
export { getDemoVaccinations } from './data/vaccinations'
export { getDemoCalendarEvents } from './data/calendar'
export { getDemoNotifications } from './data/notifications'
