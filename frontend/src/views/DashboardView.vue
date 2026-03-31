<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import { apiClient } from '@/api/client'
import type { DashboardData, Visit } from '@/types'
import type { BodyRegionKey } from '@/components/body-map/types'
import StatusBadge from '@/components/StatusBadge.vue'
import { useAuthStore } from '@/stores/auth'
import BodyMap from '@/components/body-map/BodyMap.vue'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const totalVisits = ref(0)
const activeTreatmentsCount = ref(0)
const totalTreatments = ref(0)
const recentVisits = ref<Visit[]>([])
const activeTreatments = ref<any[]>([])
const treatmentRegions = ref<string[]>([])

// Body map state
const selectedRegion = ref<BodyRegionKey | null>(null)

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function onVisitRowClick(event: { data: Visit }) {
  router.push({ name: 'visit-detail', params: { id: event.data.id } })
}

function onRegionSelect(region: BodyRegionKey | null) {
  selectedRegion.value = region
}

onMounted(async () => {
  try {
    if (!auth.user) {
      await auth.fetchUser()
    }
    const dashResponse = await apiClient.get<DashboardData>('/api/dashboard/')

    const data = dashResponse.data
    totalVisits.value = data.total_visits
    totalTreatments.value = data.total_treatments
    activeTreatmentsCount.value = data.active_treatments_count
    recentVisits.value = data.recent_visits
    activeTreatments.value = data.active_treatments
    treatmentRegions.value = data.treatment_regions
  } catch {
    // silent fail — dashboard is informational
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="dashboard">
    <h1>Головна</h1>

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
    </div>

    <!-- Body Map Section -->
    <div class="body-map-section">
      <h2>Карта тіла</h2>
      <div class="body-map-layout">
        <BodyMap
          :selected-region="selectedRegion"
          :sex="auth.user?.sex"
          :treatment-regions="treatmentRegions"
          @select="onRegionSelect"
        />
      </div>
    </div>

    <div class="dashboard-sections">
      <div class="section">
        <h2>Останні візити</h2>
        <DataTable
          :value="recentVisits"
          :loading="loading"
          @row-click="onVisitRowClick"
          rowHover
          stripedRows
          class="clickable-table"
        >
          <template #empty>Візитів не знайдено</template>
          <Column field="date" header="Дата">
            <template #body="{ data }">{{ formatDate(data.date) }}</template>
          </Column>
          <Column header="Лікар">
            <template #body="{ data }">
              <span v-if="data.position">{{ data.position.name }}</span>
              <span v-if="data.position && data.doctor"> - </span>
              <span v-if="data.doctor">{{ data.doctor }}</span>
              <span v-if="!data.position && !data.doctor">-</span>
            </template>
          </Column>
          <Column header="Процедура">
            <template #body="{ data }">{{ data.procedure?.name || '-' }}</template>
          </Column>
          <Column header="Клініка">
            <template #body="{ data }">{{ data.clinic?.name || '-' }}</template>
          </Column>
        </DataTable>
      </div>

      <div class="section">
        <h2>Активні лікування</h2>
        <DataTable
          :value="activeTreatments"
          :loading="loading"
          stripedRows
        >
          <template #empty>Активних лікувань немає</template>
          <Column field="name" header="Назва" />
          <Column field="date_start" header="Дата початку">
            <template #body="{ data }">{{ formatDate(data.date_start) }}</template>
          </Column>
          <Column field="days" header="Тривалість">
            <template #body="{ data }">{{ data.days }} дн.</template>
          </Column>
          <Column header="Статус" style="width: 130px">
            <template #body="{ data }">
              <StatusBadge :status="data.status" />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1100px;
}
.dashboard h1 {
  font-size: 1.5rem;
  font-weight: 300;
  color: #e4e4e7;
  margin-bottom: 1.5rem;
  letter-spacing: 0.02em;
}
.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}
.summary-card {
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
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
  color: #22d3ee;
  background: rgba(34, 211, 238, 0.1);
}
.treatments-icon {
  color: #22d3ee;
  background: rgba(34, 211, 238, 0.1);
}
.total-icon {
  color: #22d3ee;
  background: rgba(34, 211, 238, 0.1);
}
.card-value {
  font-size: 1.75rem;
  font-weight: 300;
  color: #e4e4e7;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}
.card-label {
  font-size: 0.75rem;
  color: #52525b;
  margin-top: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Body map section */
.body-map-section {
  margin-bottom: 2rem;
}
.body-map-section h2 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #52525b;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
.body-map-layout {
  background: #050505;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}

.dashboard-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.section h2 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #52525b;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
.clickable-table :deep(tr) {
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
