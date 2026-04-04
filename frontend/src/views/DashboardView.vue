<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { DataTablePageEvent } from 'primevue/datatable'
import { apiClient } from '@/api/client'
import type { DashboardData, Visit, Vaccination, PaginatedResponse } from '@/types'
import { useVaccinationsStore } from '@/stores/vaccinations'
import type { BodyRegionKey } from '@/components/body-map/types'
import { useAuthStore } from '@/stores/auth'
import HealthMetricModal from '@/components/HealthMetricModal.vue'
import DashboardSummaryCards from '@/components/dashboard/DashboardSummaryCards.vue'
import DashboardRecentVisits from '@/components/dashboard/DashboardRecentVisits.vue'
import DashboardActiveTreatments from '@/components/dashboard/DashboardActiveTreatments.vue'
import DashboardBodyMap from '@/components/dashboard/DashboardBodyMap.vue'

const router = useRouter()
const auth = useAuthStore()
const vaccinationsStore = useVaccinationsStore()

const loading = ref(true)
const totalVisits = ref(0)
const activeTreatmentsCount = ref(0)
const totalTreatments = ref(0)
const recentVisits = ref<Visit[]>([])
const activeTreatments = ref<any[]>([])

// Vaccination data
const upcomingVaccinations = ref<Vaccination[]>([])
const overdueVaccinations = ref<Vaccination[]>([])

// Expense data
const expensesYear = ref<number | null>(null)
const expensesTotal = ref<number | null>(null)

// Health metric modal
const metricModalVisible = ref(false)

// Body map state
const selectedRegion = ref<BodyRegionKey | null>(null)

// Modal state
const modalVisible = ref(false)
const modalVisits = ref<Visit[]>([])
const modalTotal = ref(0)
const modalPage = ref(1)
const modalPageSize = ref(10)
const modalLoading = ref(false)

async function fetchModalVisits() {
  if (!selectedRegion.value) return
  modalLoading.value = true
  try {
    const response = await apiClient.get<PaginatedResponse<Visit>>('/api/v1/visits/', {
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

function onModalRowClick(visit: Visit) {
  modalVisible.value = false
  router.push({ name: 'visit-detail', params: { id: visit.id } })
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

function onVisitRowClick(visit: Visit) {
  router.push({ name: 'visit-detail', params: { id: visit.id } })
}

function onVaccinationClick(vaccination: Vaccination) {
  router.push({ name: 'vaccination-edit', params: { id: vaccination.id } })
}

function onRegionSelect(region: BodyRegionKey | null) {
  selectedRegion.value = region
  if (region) {
    modalPage.value = 1
    modalVisible.value = true
    fetchModalVisits()
  }
}

function applyDashboardData(data: DashboardData) {
  totalVisits.value = data.total_visits
  totalTreatments.value = data.total_treatments
  activeTreatmentsCount.value = data.active_treatments_count
  recentVisits.value = data.recent_visits
  activeTreatments.value = data.active_treatments
  expensesYear.value = data.expenses_year ?? null
  expensesTotal.value = data.expenses_total ?? null
  if (data.upcoming_vaccinations) upcomingVaccinations.value = data.upcoming_vaccinations
  if (data.overdue_vaccinations) overdueVaccinations.value = data.overdue_vaccinations
}

async function onMetricSaved() {
  try {
    const dashResponse = await apiClient.get<DashboardData>('/api/v1/dashboard/')
    applyDashboardData(dashResponse.data)
  } catch {
    // silent
  }
}

onMounted(async () => {
  try {
    if (!auth.user) {
      await auth.fetchUser()
    }
    const dashResponse = await apiClient.get<DashboardData>('/api/v1/dashboard/')
    applyDashboardData(dashResponse.data)

    // Load vaccinations from dashboard or fallback to store
    const data = dashResponse.data
    if (!data.upcoming_vaccinations && !data.overdue_vaccinations) {
      try {
        await vaccinationsStore.fetchVaccinations({ status: 'upcoming', size: 10 })
        upcomingVaccinations.value = vaccinationsStore.vaccinations.filter(v => v.status === 'upcoming')
        await vaccinationsStore.fetchVaccinations({ status: 'overdue', size: 10 })
        overdueVaccinations.value = vaccinationsStore.vaccinations.filter(v => v.status === 'overdue')
      } catch {
        // silent
      }
    }
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

    <DashboardSummaryCards
      :total-visits="totalVisits"
      :active-treatments-count="activeTreatmentsCount"
      :total-treatments="totalTreatments"
      :expenses-year="expensesYear"
      :expenses-total="expensesTotal"
      @add-metric="metricModalVisible = true"
    />

    <DashboardBodyMap
      :selected-region="selectedRegion"
      :sex="auth.user?.sex"
      v-model:modal-visible="modalVisible"
      :modal-visits="modalVisits"
      :modal-total="modalTotal"
      :modal-page-size="modalPageSize"
      :modal-loading="modalLoading"
      @region-select="onRegionSelect"
      @modal-page="onModalPage"
      @modal-row-click="onModalRowClick"
      @modal-close="onModalClose"
      @add-visit-from-modal="addVisitFromModal"
    />

    <HealthMetricModal
      v-model:visible="metricModalVisible"
      @saved="onMetricSaved"
    />

    <div class="dashboard-sections">
      <DashboardRecentVisits
        :recent-visits="recentVisits"
        :loading="loading"
        :overdue-vaccinations="overdueVaccinations"
        :upcoming-vaccinations="upcomingVaccinations"
        @visit-click="onVisitRowClick"
        @vaccination-click="onVaccinationClick"
      />

      <DashboardActiveTreatments
        :active-treatments="activeTreatments"
        :loading="loading"
      />
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
.dashboard-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style>
