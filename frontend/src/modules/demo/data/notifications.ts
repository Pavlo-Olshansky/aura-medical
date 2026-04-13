// Demo notifications (Reminder shape from frontend/src/api/notifications.ts).
// >=2 fake reminders per Clarification Q2 so the bell badge renders.

import type { Reminder } from '@/api/notifications'
import { getOrCreate } from '../cache'
import { getDemoVisits } from './visits'
import { getDemoVaccinations } from './vaccinations'

export function getDemoNotifications(): Reminder[] {
  return getOrCreate<Reminder[]>('notifications', () => {
    const items: Reminder[] = []
    const tomorrow = new Date(Date.now() + 86_400_000).toISOString().slice(0, 10)
    const lastWeek = new Date(Date.now() - 7 * 86_400_000).toISOString().slice(0, 10)

    // Pick the most recent visit as a fake "upcoming" reminder.
    const recentVisit = getDemoVisits()[0]
    if (recentVisit) {
      items.push({
        entity_type: 'visit',
        entity_id: recentVisit.id,
        reminder_type: 'upcoming',
        title: `Завтра візит до ${recentVisit.doctor || 'лікаря'}`,
        event_date: tomorrow,
        route: `/visits/${recentVisit.id}`,
      })
    }

    // Overdue vaccination reminder (works even without vaccination data).
    const vaccinations = getDemoVaccinations()
    const vacc = vaccinations[0]
    items.push({
      entity_type: 'vaccination',
      entity_id: vacc?.id ?? 1,
      reminder_type: 'overdue',
      title: 'Вакцинація прострочена',
      event_date: lastWeek,
      route: '/vaccinations',
    })

    return items
  })
}
