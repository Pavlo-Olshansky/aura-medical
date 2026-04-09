<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'
import type { CalendarEvent } from '@/types'

const props = defineProps<{
  event: CalendarEvent | null
  visible: boolean
  position: { top: number; left: number }
}>()

const emit = defineEmits<{
  close: []
  navigate: [url: string]
  edit: [event: CalendarEvent]
  exportIcs: [id: number]
}>()

const isVisit = computed(() => props.event?.event_type === 'visit')
const isFuture = computed(() => {
  if (!props.event) return false
  return new Date(props.event.start) > new Date()
})

function handleNavigate() {
  if (props.event) emit('navigate', props.event.url)
}

function handleEdit() {
  if (props.event) emit('edit', props.event)
}

function handleExportIcs() {
  if (props.event && isVisit.value) emit('exportIcs', props.event.id)
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible && event"
      class="popover-overlay"
      @click.self="emit('close')"
    >
      <div
        class="event-popover"
        :style="{ top: position.top + 'px', left: position.left + 'px' }"
      >
        <div class="popover-header">
          <span class="event-type-badge" :style="{ background: event.color }">
            {{ event.event_type === 'visit' ? 'Візит' : 'Лікування' }}
          </span>
          <button class="close-btn" @click="emit('close')">
            <i class="pi pi-times" />
          </button>
        </div>

        <h3 class="event-title">{{ event.title }}</h3>

        <div class="event-details">
          <div v-if="event.extra.procedure" class="detail-row">
            <span class="detail-label">Процедура</span>
            <span>{{ event.extra.procedure }}</span>
          </div>
          <div v-if="event.extra.clinic" class="detail-row">
            <span class="detail-label">Клініка</span>
            <span>{{ event.extra.clinic }}</span>
          </div>
          <div v-if="event.extra.city" class="detail-row">
            <span class="detail-label">Місто</span>
            <span>{{ event.extra.city }}</span>
          </div>
          <div v-if="event.extra.body_region" class="detail-row">
            <span class="detail-label">Ділянка</span>
            <span>{{ event.extra.body_region }}</span>
          </div>
          <div v-if="event.extra.doctor" class="detail-row">
            <span class="detail-label">Лікар</span>
            <span>{{ event.extra.doctor }}</span>
          </div>
        </div>

        <div class="popover-actions">
          <Button
            label="Детальніше"
            icon="pi pi-eye"
            size="small"
            text
            @click="handleNavigate"
          />
          <Button
            v-if="isVisit"
            label="Редагувати"
            icon="pi pi-pencil"
            size="small"
            text
            @click="handleEdit"
          />
          <Button
            v-if="isVisit"
            label=".ics"
            icon="pi pi-download"
            size="small"
            text
            @click="handleExportIcs"
          />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.popover-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
}
.event-popover {
  position: fixed;
  background: var(--bg-sidebar);
  border: 1px solid var(--border-subtle);
  border-radius: 0.5rem;
  padding: 1rem;
  min-width: 260px;
  max-width: 340px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  z-index: 1001;
}
.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.event-type-badge {
  font-size: 0.7rem;
  font-weight: 600;
  color: #fff;
  padding: 0.15rem 0.5rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.close-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  font-size: 0.875rem;
}
.event-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem;
}
.event-details {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}
.detail-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}
.detail-label {
  color: var(--text-faint);
  min-width: 70px;
}
.popover-actions {
  display: flex;
  gap: 0.25rem;
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.5rem;
}
</style>
