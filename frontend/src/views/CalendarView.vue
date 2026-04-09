<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import ukLocale from '@fullcalendar/core/locales/uk'
import type { EventClickArg, DatesSetArg, EventInput } from '@fullcalendar/core'
import type { DateClickArg } from '@fullcalendar/interaction'
import Button from 'primevue/button'
import CalendarEventPopover from '@/components/CalendarEventPopover.vue'
import CalendarSidePanel from '@/components/CalendarSidePanel.vue'
import type { CalendarEvent } from '@/types'
import { getCalendarEvents } from '@/api/calendar'
import { apiClient } from '@/api/client'

const router = useRouter()
const calendarRef = ref()

// Popover state
const popoverVisible = ref(false)
const popoverEvent = ref<CalendarEvent | null>(null)
const popoverPosition = ref({ top: 0, left: 0 })

// Side panel state
const sidePanelVisible = ref(false)
const sidePanelDate = ref<Date | null>(null)
const sidePanelVisitId = ref<number | null>(null)

// Calendar events cache for refetch
const lastFetchStart = ref('')
const lastFetchEnd = ref('')

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: ukLocale,
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek',
  },
  height: 'auto',
  events: fetchEvents,
  eventClick: handleEventClick,
  dateClick: handleDateClick,
  datesSet: handleDatesSet,
  eventDisplay: 'block',
  dayMaxEvents: 3,
  nowIndicator: true,
})

let currentDatesSetInfo: DatesSetArg | null = null

function handleDatesSet(info: DatesSetArg) {
  currentDatesSetInfo = info
  lastFetchStart.value = formatDateParam(info.start)
  lastFetchEnd.value = formatDateParam(info.end)
}

async function fetchEvents(
  info: { start: Date; end: Date },
  successCallback: (events: EventInput[]) => void,
  failureCallback: (error: Error) => void,
) {
  try {
    const dateFrom = formatDateParam(info.start)
    const dateTo = formatDateParam(info.end)
    const data = await getCalendarEvents(dateFrom, dateTo)

    const events: EventInput[] = data.events.map((e) => ({
      id: `${e.event_type}-${e.id}`,
      title: e.title,
      start: e.start,
      end: e.end,
      allDay: e.all_day,
      color: e.color,
      classNames: e.event_type === 'treatment' ? ['fc-treatment-event'] : [],
      extendedProps: {
        calendarEvent: e,
      },
    }))
    successCallback(events)
  } catch (err) {
    failureCallback(err as Error)
  }
}

function handleEventClick(info: EventClickArg) {
  info.jsEvent.preventDefault()
  const calEvent: CalendarEvent = info.event.extendedProps.calendarEvent
  popoverEvent.value = calEvent

  const rect = info.el.getBoundingClientRect()
  const popoverWidth = 300
  let left = rect.right + 8
  if (left + popoverWidth > window.innerWidth) {
    left = rect.left - popoverWidth - 8
  }
  popoverPosition.value = {
    top: Math.min(rect.top, window.innerHeight - 300),
    left: Math.max(8, left),
  }
  popoverVisible.value = true
}

function handleDateClick(info: DateClickArg) {
  popoverVisible.value = false
  sidePanelVisitId.value = null
  sidePanelDate.value = info.date
  sidePanelVisible.value = true
}

function closePopover() {
  popoverVisible.value = false
  popoverEvent.value = null
}

function handlePopoverNavigate(url: string) {
  closePopover()
  router.push(url)
}

function handlePopoverEdit(event: CalendarEvent) {
  closePopover()
  if (event.event_type === 'visit') {
    sidePanelVisitId.value = event.id
    sidePanelDate.value = null
    sidePanelVisible.value = true
  }
}

async function handleExportIcs(visitId: number) {
  closePopover()
  const response = await apiClient.get(`/api/v1/visits/${visitId}/ics`, {
    responseType: 'blob',
  })
  const blob = new Blob([response.data], { type: 'text/calendar' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `visit-${visitId}.ics`
  a.click()
  URL.revokeObjectURL(url)
}

function handleSidePanelSaved() {
  sidePanelVisible.value = false
  refetchEvents()
}

function handleSidePanelDeleted() {
  sidePanelVisible.value = false
  refetchEvents()
}

function refetchEvents() {
  const api = calendarRef.value?.getApi()
  if (api) {
    api.refetchEvents()
  }
}

function formatDateParam(d: Date): string {
  return d.toISOString().split('T')[0]!
}

function handleAddAppointment() {
  sidePanelVisitId.value = null
  sidePanelDate.value = new Date()
  sidePanelVisible.value = true
}

onMounted(() => {
  // Close popover on escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (popoverVisible.value) closePopover()
    }
  })
})
</script>

<template>
  <div class="calendar-page">
    <div class="page-header">
      <h1>Календар</h1>
      <Button
        label="Додати візит"
        icon="pi pi-plus"
        @click="handleAddAppointment"
      />
    </div>

    <div class="calendar-container">
      <FullCalendar ref="calendarRef" :options="calendarOptions" />
    </div>

    <CalendarEventPopover
      :event="popoverEvent"
      :visible="popoverVisible"
      :position="popoverPosition"
      @close="closePopover"
      @navigate="handlePopoverNavigate"
      @edit="handlePopoverEdit"
      @export-ics="handleExportIcs"
    />

    <CalendarSidePanel
      :visible="sidePanelVisible"
      :date="sidePanelDate"
      :visit-id="sidePanelVisitId"
      @close="sidePanelVisible = false"
      @saved="handleSidePanelSaved"
      @deleted="handleSidePanelDeleted"
    />
  </div>
</template>

<style scoped>
.calendar-page {
  max-width: 1200px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}
.calendar-container {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--border-subtle);
}

/* FullCalendar theme overrides */
:deep(.fc) {
  --fc-border-color: var(--border-subtle);
  --fc-page-bg-color: transparent;
  --fc-neutral-bg-color: rgba(255, 255, 255, 0.02);
  --fc-today-bg-color: rgba(var(--accent-rgb, 99, 102, 241), 0.08);
  --fc-event-border-color: transparent;
}
:deep(.fc .fc-toolbar-title) {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}
:deep(.fc .fc-button) {
  background: var(--bg-hover);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  text-transform: capitalize;
}
:deep(.fc .fc-button:hover) {
  background: var(--bg-active);
  color: var(--text-primary);
}
:deep(.fc .fc-button-active) {
  background: var(--accent) !important;
  color: #fff !important;
  border-color: var(--accent) !important;
}
:deep(.fc .fc-col-header-cell) {
  padding: 0.5rem 0;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-faint);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
:deep(.fc .fc-daygrid-day-number) {
  color: var(--text-secondary);
  font-size: 0.875rem;
  padding: 0.35rem 0.5rem;
}
:deep(.fc .fc-daygrid-day.fc-day-today .fc-daygrid-day-number) {
  color: var(--accent);
  font-weight: 700;
}
:deep(.fc .fc-event) {
  border-radius: 2px;
  font-size: 0.75rem;
  padding: 1px 4px;
  cursor: pointer;
}
:deep(.fc .fc-daygrid-event-dot) {
  display: none;
}
:deep(.fc .fc-more-link) {
  color: var(--accent);
  font-size: 0.75rem;
}
:deep(.fc-treatment-event) {
  opacity: 0.45;
  font-style: italic;
  border-left: 2px dashed rgba(255, 167, 38, 0.7) !important;
  font-size: 0.7rem !important;
}

/* Mobile: show dots instead of full event blocks */
@media (max-width: 768px) {
  .calendar-container {
    padding: 0.5rem;
  }
  :deep(.fc .fc-daygrid-event) {
    font-size: 0;
    height: 6px;
    margin: 1px 2px;
    min-height: 6px;
    border-radius: 3px;
  }
  :deep(.fc .fc-toolbar) {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
