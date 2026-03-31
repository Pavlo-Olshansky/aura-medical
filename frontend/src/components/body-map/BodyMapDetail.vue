<script setup lang="ts">
import { computed } from 'vue'
import type { BodyRegionDetailResponse } from './types'
import StatusBadge from '@/components/StatusBadge.vue'

const props = defineProps<{
  detail: BodyRegionDetailResponse | null
  loading: boolean
}>()

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const hasData = computed(() => {
  if (!props.detail) return false
  return props.detail.visits.length > 0 || props.detail.treatments.length > 0
})
</script>

<template>
  <div class="body-map-detail">
    <template v-if="loading">
      <div class="detail-loading">Завантаження...</div>
    </template>
    <template v-else-if="detail">
      <h3 class="detail-title">{{ detail.label }}</h3>

      <template v-if="hasData">
        <div v-if="detail.visits.length > 0" class="detail-section">
          <h4>Візити ({{ detail.visits.length }})</h4>
          <div
            v-for="visit in detail.visits"
            :key="visit.id"
            class="detail-item"
          >
            <div class="item-date">{{ formatDate(visit.date) }}</div>
            <div class="item-info">
              <span v-if="visit.position_name">{{ visit.position_name }}</span>
              <span v-if="visit.position_name && visit.doctor"> — </span>
              <span v-if="visit.doctor">{{ visit.doctor }}</span>
            </div>
            <div v-if="visit.procedure_name" class="item-secondary">
              {{ visit.procedure_name }}
            </div>
            <div v-if="visit.clinic_name" class="item-secondary">
              {{ visit.clinic_name }}
            </div>
          </div>
        </div>

        <div v-if="detail.treatments.length > 0" class="detail-section">
          <h4>Лікування ({{ detail.treatments.length }})</h4>
          <div
            v-for="treatment in detail.treatments"
            :key="treatment.id"
            class="detail-item"
          >
            <div class="item-row">
              <span class="item-name">{{ treatment.name }}</span>
              <StatusBadge :status="treatment.status" />
            </div>
            <div class="item-secondary">
              {{ formatDate(treatment.date_start) }} — {{ formatDate(treatment.date_end) }}
              ({{ treatment.days }} дн.)
            </div>
          </div>
        </div>
      </template>

      <div v-else class="detail-empty">
        Немає даних для цієї ділянки
      </div>
    </template>
  </div>
</template>

<style scoped>
.body-map-detail {
  padding: 0.5rem;
}
.detail-loading {
  color: #52525b;
  font-size: 0.8125rem;
  text-align: center;
  padding: 2rem 0;
}
.detail-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #e4e4e7;
  margin: 0 0 1rem;
}
.detail-section {
  margin-bottom: 1.25rem;
}
.detail-section h4 {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #52525b;
  margin: 0 0 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.detail-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.detail-item:last-child {
  border-bottom: none;
}
.item-date {
  font-size: 0.75rem;
  font-weight: 600;
  color: #a1a1aa;
}
.item-info {
  font-size: 0.8125rem;
  color: #d4d4d8;
}
.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.item-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #d4d4d8;
}
.item-secondary {
  font-size: 0.75rem;
  color: #52525b;
  margin-top: 0.125rem;
}
.detail-empty {
  color: #3f3f46;
  font-size: 0.8125rem;
  text-align: center;
  padding: 2rem 0;
}
</style>
