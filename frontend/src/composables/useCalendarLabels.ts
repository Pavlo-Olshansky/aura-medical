import type { CalendarEvent } from '@/types'

export function getEventLabel(event: CalendarEvent): string {
  if (event.event_type === 'treatment') return event.title

  const { procedure, position, body_region, clinic } = event.extra
  if (procedure && clinic) return `${procedure} — ${clinic}`
  if (position && clinic) return `${position} — ${clinic}`
  if (body_region && clinic) return `${body_region} — ${clinic}`
  if (clinic) return clinic
  if (procedure) return procedure
  if (position) return position
  return 'Візит'
}
