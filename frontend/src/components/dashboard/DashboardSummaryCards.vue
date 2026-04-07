<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import type { WeatherSummary } from '@/types/weather'
import { getStormColor } from '@/utils/weatherUtils'

const router = useRouter()

const props = defineProps<{
  totalVisits: number
  activeTreatmentsCount: number
  totalTreatments: number
  expensesYear: number | null
  expensesTotal: number | null
  weather: WeatherSummary | null
}>()

defineEmits<{
  (e: 'add-metric'): void
}>()

const showStormWarning = computed(() =>
  props.weather?.kp_index != null && props.weather.kp_index >= 4,
)

const stormTooltip = computed(() => {
  if (!props.weather?.kp_index) return ''
  const severity = props.weather.storm_severity
  const kp = props.weather.kp_index
  const advisory = `Kp ${kp} — може впливати на самопочуття`
  return severity ? `Магнітна буря: ${severity}\n${advisory}` : advisory
})
</script>

<template>
  <div class="summary-row">
    <div class="summary-cards">
      <Card class="summary-card">
        <template #content>
          <div class="card-content">
            <i class="pi pi-calendar card-icon visits-icon" />
            <div>
              <div class="card-value">{{ totalVisits }}</div>
              <div class="card-label">Всього візитів</div>
            </div>
          </div>
        </template>
      </Card>

      <Card class="summary-card">
        <template #content>
          <div class="card-content">
            <i class="pi pi-heart card-icon treatments-icon" />
            <div>
              <div class="card-value">{{ activeTreatmentsCount }}</div>
              <div class="card-label">Активних лікувань</div>
            </div>
          </div>
        </template>
      </Card>

      <Card class="summary-card">
        <template #content>
          <div class="card-content">
            <i class="pi pi-list card-icon total-icon" />
            <div>
              <div class="card-value">{{ totalTreatments }}</div>
              <div class="card-label">Всього лікувань</div>
            </div>
          </div>
        </template>
      </Card>

      <Card v-if="expensesYear != null" class="summary-card">
        <template #content>
          <div class="card-content">
            <i class="pi pi-wallet card-icon expenses-icon" />
            <div>
              <div class="card-value">{{ expensesYear }} <span class="card-currency">грн</span></div>
              <div class="card-label">Витрати за рік</div>
            </div>
          </div>
        </template>
      </Card>

      <Card v-if="weather" class="summary-card weather-card" @click="router.push('/weather')">
        <template #content>
          <div class="card-content">
            <i class="pi pi-cloud card-icon weather-icon" />
            <div>
              <div class="card-value">
                {{ Math.round(weather.temperature) }}°
                <i
                  v-if="showStormWarning"
                  v-tooltip.top="stormTooltip"
                  class="pi pi-exclamation-triangle storm-warn"
                  :style="{ color: getStormColor(weather.kp_index!) }"
                />
              </div>
              <div class="card-label">{{ weather.condition_description }}</div>
            </div>
          </div>
        </template>
      </Card>
    </div>
    <div class="quick-actions">
      <Button
        label="Додати показник"
        icon="pi pi-plus"
        severity="secondary"
        outlined
        @click="$emit('add-metric')"
      />
    </div>
  </div>
</template>

<style scoped>
.summary-row {
  margin-bottom: 2rem;
}
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1rem;
}
.quick-actions {
  display: flex;
  gap: 0.75rem;
}
.summary-card {
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
}
.summary-card :deep(.p-card-body) {
  background: transparent;
}
.summary-card :deep(.p-card-content) {
  background: transparent;
}
.card-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.card-icon {
  font-size: 2rem;
  padding: 0.75rem;
  border-radius: 4px;
}
.visits-icon {
  color: var(--accent);
  background: rgba(34, 211, 238, 0.1);
}
.treatments-icon {
  color: var(--accent);
  background: rgba(34, 211, 238, 0.1);
}
.total-icon {
  color: var(--accent);
  background: rgba(34, 211, 238, 0.1);
}
.expenses-icon {
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.1);
}
.card-currency {
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--text-muted);
}
.card-value {
  font-size: 1.75rem;
  font-weight: 300;
  color: var(--text-primary);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}
.card-label {
  font-size: 0.75rem;
  color: var(--text-faint);
  margin-top: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.weather-card {
  cursor: pointer;
  transition: border-color 0.2s;
}
.weather-card:hover {
  border-color: rgba(34, 211, 238, 0.3);
}
.weather-icon {
  color: var(--accent);
  background: rgba(34, 211, 238, 0.1);
}
.storm-warn {
  font-size: 0.85rem;
  margin-left: 0.35rem;
  vertical-align: middle;
  cursor: help;
}
@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
