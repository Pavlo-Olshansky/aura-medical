<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import type { DataTablePageEvent } from 'primevue/datatable'
import { apiClient } from '@/api/client'
import type { DashboardData, Visit, PaginatedResponse } from '@/types'
import type { BodyRegionKey } from '@/components/body-map/types'
import { BODY_REGION_LABELS } from '@/components/body-map/body-regions'
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

// Modal state
const modalVisible = ref(false)
const modalVisits = ref<Visit[]>([])
const modalTotal = ref(0)
const modalPage = ref(1)
const modalPageSize = ref(10)
const modalLoading = ref(false)

const modalHeader = computed(() => {
  if (!selectedRegion.value) return ''
  const label = BODY_REGION_LABELS[selectedRegion.value] || selectedRegion.value
  return `${label} — Візити`
})

async function fetchModalVisits() {
  if (!selectedRegion.value) return
  modalLoading.value = true
  try {
    const response = await apiClient.get<PaginatedResponse<Visit>>('/api/visits/', {
      params: {
        body_region: selectedRegion.value,
        page: modalPage.value,
        size: modalPageSize.value,
        sort_by: 'date',
        sort_order: 'desc',
      },
    })
    modalVisits.value = response.data.items
    modalTotal.value = response.data.total
  } catch {
    modalVisits.value = []
    modalTotal.value = 0
  } finally {
    modalLoading.value = false
  }
}

function onModalPage(event: DataTablePageEvent) {
  modalPage.value = event.page + 1
  modalPageSize.value = event.rows
  fetchModalVisits()
}

function onModalRowClick(event: { data: Visit }) {
  modalVisible.value = false
  router.push({ name: 'visit-detail', params: { id: event.data.id } })
}

function onModalClose() {
  selectedRegion.value = null
  modalVisits.value = []
  modalTotal.value = 0
  modalPage.value = 1
}

function addVisitFromModal() {
  modalVisible.value = false
  router.push({ name: 'visit-create', query: { body_region: selectedRegion.value || undefined } })
}

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
    modalPage.value = 1
    modalVisible.value = true
    fetchModalVisits()
  }
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

    <!-- Body Region Visits Modal -->
    <Dialog
      v-model:visible="modalVisible"
      :header="modalHeader"
      modal
      dismissableMask
      :style="{ width: '900px' }"
      :breakpoints="{ '960px': '95vw' }"
      @hide="onModalClose"
    >
      <div class="modal-toolbar">
        <Button label="Додати візит" icon="pi pi-plus" @click="addVisitFromModal" />
      </div>
      <DataTable
        :value="modalVisits"
        :loading="modalLoading"
        :lazy="true"
        :paginator="true"
        :rows="modalPageSize"
        :totalRecords="modalTotal"
        :rowsPerPageOptions="[10, 20, 50]"
        @page="onModalPage"
        @row-click="onModalRowClick"
        rowHover
        stripedRows
        class="clickable-table"
      >
        <template #empty>Немає візитів для цієї ділянки</template>
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
        <Column header="Місто">
          <template #body="{ data }">{{ data.city?.name || '-' }}</template>
        </Column>
        <Column header="Документ" style="width: 80px; text-align: center">
          <template #body="{ data }">
            <i v-if="data.document || data.has_document" class="pi pi-file" style="color: #2563eb" />
            <span v-else>-</span>
          </template>
        </Column>
      </DataTable>
    </Dialog>

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
.modal-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
