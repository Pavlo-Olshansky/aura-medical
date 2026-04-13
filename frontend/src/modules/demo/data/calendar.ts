// Calendar events derived from demo visits + treatment-start dates.
// Filtered to the requested date range.

import type { CalendarEvent } from '@/types'
import { getDemoVisits } from './visits'
import { getDemoTreatments } from './treatments'

export function getDemoCalendarEvents(from: string, to: string): CalendarEvent[] {
  const events: CalendarEvent[] = []
  let nextId = 1

  for (const visit of getDemoVisits()) {
    if (visit.date >= from && visit.date <= to) {
      events.push({
        id: nextId++,
        event_type: 'visit',
        title: visit.doctor || visit.procedure?.name || 'Візит',
        start: visit.date,
        end: visit.date,
        all_day: true,
        color: '#3b82f6',
        url: `/visits/${visit.id}`,
        extra: {
          clinic: visit.clinic?.name || '',
          city: visit.city?.name || '',
        },
      })
    }
  }

  for (const treatment of getDemoTreatments()) {
    if (treatment.date_start >= from && treatment.date_start <= to) {
      events.push({
        id: nextId++,
        event_type: 'treatment',
        title: `Початок: ${treatment.name}`,
        start: treatment.date_start,
        end: treatment.date_start,
        all_day: true,
        color: '#10b981',
        url: `/treatments`,
        extra: {
          days: String(treatment.days),
        },
      })
    }
  }

  return events
}
