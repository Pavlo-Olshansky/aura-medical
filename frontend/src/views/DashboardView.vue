<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import { apiClient } from '@/api/client'
import type { DashboardData, Visit, Treatment } from '@/types'
import StatusBadge from '@/components/StatusBadge.vue'

const router = useRouter()

const loading = ref(true)
const totalVisits = ref(0)
const activeTreatmentsCount = ref(0)
const totalTreatments = ref(0)
const recentVisits = ref<Visit[]>([])
const activeTreatments = ref<Treatment[]>([])

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function onVisitRowClick(event: { data: Visit }) {
  router.push({ name: 'visit-detail', params: { id: event.data.id } })
}

onMounted(async () => {
  try {
    const response = await apiClient.get<DashboardData>('/api/dashboard/')
    const data = response.data
    totalVisits.value = data.total_visits
    totalTreatments.value = data.total_treatments
    activeTreatmentsCount.value = data.active_treatments_count
    recentVisits.value = data.recent_visits
    activeTreatments.value = data.active_treatments
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
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 1.5rem;
}
.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}
.summary-card {
  border-radius: 0.75rem;
}
.card-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.card-icon {
  font-size: 2rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
}
.visits-icon {
  color: #2563eb;
  background: #dbeafe;
}
.treatments-icon {
  color: #16a34a;
  background: #dcfce7;
}
.total-icon {
  color: #9333ea;
  background: #f3e8ff;
}
.card-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}
.card-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
}
.dashboard-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.section h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1rem;
}
.clickable-table :deep(tr) {
  cursor: pointer;
}
</style>
