<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { DataTablePageEvent } from 'primevue/datatable'
import { apiClient } from '@/api/client'
import { getWeatherSummary } from '@/api/weather'
import type { DashboardData, Visit, Vaccination, PaginatedResponse } from '@/types'
import type { WeatherSummary } from '@/types/weather'
import { useVaccinationsStore } from '@/stores/vaccinations'
import type { BodyRegionKey } from '@/components/body-map/types'
import { useAuthStore } from '@/stores/auth'
import HealthMetricModal from '@/components/HealthMetricModal.vue'
import DashboardSummaryCards from '@/components/dashboard/DashboardSummaryCards.vue'
import DashboardRecentVisits from '@/components/dashboard/DashboardRecentVisits.vue'
import DashboardActiveTreatments from '@/components/dashboard/DashboardActiveTreatments.vue'
import DashboardBodyMap from '@/components/dashboard/DashboardBodyMap.vue'
import NotificationBanner from '@/components/NotificationBanner.vue'
import { getTestMode, sendTestPush } from '@/api/push'

const router = useRouter()
const auth = useAuthStore()
const vaccinationsStore = useVaccinationsStore()

const loading = ref(true)
const testMode = ref(false)
const testPushSending = ref(false)
const testPushMessage = ref('')
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

// Weather data
const weatherSummary = ref<WeatherSummary | null>(null)

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

async function handleTestPush() {
  testPushSending.value = true
  testPushMessage.value = ''
  try {
    const result = await sendTestPush()
    testPushMessage.value = `Сповіщення прийде через ${result.delay_seconds} сек`
  } catch {
    testPushMessage.value = 'Помилка. Перевірте підписку на push.'
  } finally {
    testPushSending.value = false
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
    // Auto-detect city on first load if user has no city set and auto is on
    try {
      const profile = await apiClient.get<{ weather_city: string | null; weather_city_auto: boolean }>('/api/v1/profile/')
      if (!profile.data.weather_city && profile.data.weather_city_auto) {
        await apiClient.post('/api/v1/weather/detect-city')
      }
    } catch {
      // silent
    }
    try {
      weatherSummary.value = await getWeatherSummary()
    } catch {
      // Weather unavailable — card will be hidden
    }
    try {
      testMode.value = await getTestMode()
    } catch {
      // silent
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
    <NotificationBanner />
    <div v-if="testMode" class="test-push-bar">
      <button class="test-push-btn" @click="handleTestPush" :disabled="testPushSending">
        <i class="pi pi-bell" />
        {{ testPushSending ? 'Заплановано...' : 'Тестове push-сповіщення (30 сек)' }}
      </button>
      <span v-if="testPushMessage" class="test-push-msg">{{ testPushMessage }}</span>
    </div>
    <h1>Головна</h1>

    <DashboardSummaryCards
      :total-visits="totalVisits"
      :active-treatments-count="activeTreatmentsCount"
      :total-treatments="totalTreatments"
      :expenses-year="expensesYear"
      :expenses-total="expensesTotal"
      :weather="weatherSummary"
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
.test-push-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.test-push-btn {
  background: var(--bg-card);
  border: 1px dashed var(--accent);
  color: var(--accent);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: opacity 0.15s;
}
.test-push-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.test-push-btn:hover:not(:disabled) {
  background: var(--bg-hover);
}
.test-push-msg {
  font-size: 0.8125rem;
  color: var(--text-muted);
}
.dashboard {
  max-width: 1100px;
}
.dashboard h1 {
  font-size: 1.5rem;
  font-weight: 300;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  letter-spacing: 0.02em;
}
.dashboard-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style>
