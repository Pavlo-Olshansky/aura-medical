<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import Sidebar from 'primevue/sidebar'
import { apiClient } from '@/api/client'
import type { DashboardData, Visit, Treatment } from '@/types'
import type { BodyMapSummaryResponse, BodyRegionDetailResponse, BodyRegionKey } from '@/components/body-map/types'
import StatusBadge from '@/components/StatusBadge.vue'
import BodyMap from '@/components/body-map/BodyMap.vue'
import BodyMapDetail from '@/components/body-map/BodyMapDetail.vue'
import BodyMapLegend from '@/components/body-map/BodyMapLegend.vue'

const router = useRouter()

const loading = ref(true)
const totalVisits = ref(0)
const activeTreatmentsCount = ref(0)
const totalTreatments = ref(0)
const recentVisits = ref<Visit[]>([])
const activeTreatments = ref<Treatment[]>([])

// Body map state
const bodyMapSummary = ref<BodyMapSummaryResponse>({ regions: {}, unmapped_visit_count: 0, whole_body_visit_count: 0 })
const selectedRegion = ref<BodyRegionKey | null>(null)
const regionDetail = ref<BodyRegionDetailResponse | null>(null)
const detailLoading = ref(false)
const mobileDetailVisible = ref(false)

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function onVisitRowClick(event: { data: Visit }) {
  router.push({ name: 'visit-detail', params: { id: event.data.id } })
}

function onRegionSelect(region: BodyRegionKey | null) {
  selectedRegion.value = region
  if (region) {
    mobileDetailVisible.value = true
  } else {
    mobileDetailVisible.value = false
    regionDetail.value = null
  }
}

async function fetchRegionDetail(region: BodyRegionKey) {
  detailLoading.value = true
  try {
    const response = await apiClient.get<BodyRegionDetailResponse>(`/api/dashboard/body-map/${region}/`)
    regionDetail.value = response.data
  } catch {
    regionDetail.value = null
  } finally {
    detailLoading.value = false
  }
}

watch(selectedRegion, (region) => {
  if (region) {
    fetchRegionDetail(region)
  } else {
    regionDetail.value = null
  }
})

onMounted(async () => {
  try {
    const [dashResponse, bodyMapResponse] = await Promise.all([
      apiClient.get<DashboardData>('/api/dashboard/'),
      apiClient.get<BodyMapSummaryResponse>('/api/dashboard/body-map/'),
    ])

    const data = dashResponse.data
    totalVisits.value = data.total_visits
    totalTreatments.value = data.total_treatments
    activeTreatmentsCount.value = data.active_treatments_count
    recentVisits.value = data.recent_visits
    activeTreatments.value = data.active_treatments

    bodyMapSummary.value = bodyMapResponse.data
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
        <div class="body-map-left">
          <BodyMap
            :regions="bodyMapSummary.regions"
            :selected-region="selectedRegion"
            @select="onRegionSelect"
          />
          <BodyMapLegend
            :unmapped-count="bodyMapSummary.unmapped_visit_count"
            :whole-body-count="bodyMapSummary.whole_body_visit_count"
          />
        </div>

        <!-- Desktop detail panel -->
        <div v-if="selectedRegion" class="body-map-right desktop-only">
          <BodyMapDetail :detail="regionDetail" :loading="detailLoading" />
        </div>

        <!-- Mobile bottom sheet -->
        <Sidebar
          v-model:visible="mobileDetailVisible"
          position="bottom"
          class="mobile-only-sidebar"
          :showCloseIcon="true"
          @hide="selectedRegion = null"
        >
          <BodyMapDetail :detail="regionDetail" :loading="detailLoading" />
        </Sidebar>
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
  display: flex;
  gap: 0;
  align-items: stretch;
  background: #050505;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}
.body-map-left {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.body-map-right {
  flex: 0 0 300px;
  max-height: 500px;
  overflow-y: auto;
  border-left: 1px solid rgba(255, 255, 255, 0.05);
  background: #080808;
  padding: 1rem;
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
  .body-map-layout {
    flex-direction: column;
    align-items: stretch;
  }
  .body-map-left {
    width: 100%;
  }
  .body-map-right {
    flex: none;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }
  .desktop-only {
    display: none;
  }
}

@media (min-width: 769px) {
  .mobile-only-sidebar {
    display: none !important;
  }
}
</style>
