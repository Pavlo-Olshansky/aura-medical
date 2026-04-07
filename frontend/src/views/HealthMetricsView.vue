<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import type { DataTablePageEvent } from 'primevue/datatable'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import { useToast } from 'primevue/usetoast'
import { useHealthMetricsStore } from '@/stores/healthMetrics'
import type { MetricType, HealthMetric } from '@/types'
import type { MetricTrendPoint } from '@/api/healthMetrics'
import MetricChart from '@/components/MetricChart.vue'
import HealthMetricModal from '@/components/HealthMetricModal.vue'
import { formatDate } from '@/utils/dateUtils'

const route = useRoute()
const router = useRouter()
const healthMetricsStore = useHealthMetricsStore()
const confirm = useConfirm()
const toast = useToast()

const selectedType = ref<MetricType | null>(null)
const trendData = ref<MetricTrendPoint[]>([])
const trendLoading = ref(false)

const currentPage = ref(1)
const pageSize = ref(20)

const modalVisible = ref(false)

function formatDateTime(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatValue(metric: HealthMetric): string {
  if (metric.metric_type?.has_secondary_value && metric.secondary_value != null) {
    return `${metric.value} / ${metric.secondary_value}`
  }
  return String(metric.value)
}

const showSecondaryColumn = computed(() => {
  return selectedType.value?.has_secondary_value ?? false
})

function updateUrl() {
  const query: Record<string, string> = {}
  if (selectedType.value) query.metric_type_id = String(selectedType.value.id)
  if (currentPage.value !== 1) query.page = String(currentPage.value)
  if (pageSize.value !== 20) query.size = String(pageSize.value)
  router.replace({ query })
}

async function selectType(type: MetricType) {
  selectedType.value = type
  currentPage.value = 1
  updateUrl()
  await Promise.all([loadMetrics(), loadTrend()])
}

async function loadMetrics() {
  if (!selectedType.value) return
  await healthMetricsStore.fetchHealthMetrics({
    metric_type_id: selectedType.value.id,
    page: currentPage.value,
    size: pageSize.value,
    sort_by: 'date',
    sort_order: 'desc',
  })
}

async function loadTrend() {
  if (!selectedType.value) return
  trendLoading.value = true
  try {
    trendData.value = await healthMetricsStore.fetchMetricTrend({
      metric_type_id: selectedType.value.id,
    })
  } catch {
    trendData.value = []
  } finally {
    trendLoading.value = false
  }
}

function onPage(event: DataTablePageEvent) {
  currentPage.value = event.page + 1
  pageSize.value = event.rows
  updateUrl()
  loadMetrics()
}

function confirmDelete(metric: HealthMetric) {
  confirm.require({
    message: `Ви впевнені, що хочете видалити цей показник від ${formatDate(metric.date)}?`,
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await healthMetricsStore.deleteHealthMetric(metric.id)
        toast.add({
          severity: 'success',
          summary: 'Видалено',
          detail: 'Показник успішно видалено',
          life: 3000,
        })
        await Promise.all([loadMetrics(), loadTrend()])
      } catch (e: unknown) {
        const err = e as { response?: { data?: { detail?: string } } }
        toast.add({
          severity: 'error',
          summary: 'Помилка',
          detail: err.response?.data?.detail || 'Не вдалося видалити показник',
          life: 5000,
        })
      }
    },
  })
}

async function onModalSaved() {
  if (selectedType.value) {
    await Promise.all([loadMetrics(), loadTrend()])
  }
}

onMounted(async () => {
  await healthMetricsStore.fetchMetricTypes()

  // Restore type from URL or default to first
  const urlTypeId = route.query.metric_type_id ? parseInt(route.query.metric_type_id as string, 10) : null
  const urlPage = route.query.page ? parseInt(route.query.page as string, 10) : 1
  const urlSize = route.query.size ? parseInt(route.query.size as string, 10) : 20

  if (urlPage > 0) currentPage.value = urlPage
  if (urlSize > 0) pageSize.value = urlSize

  let typeToSelect: MetricType | undefined
  if (urlTypeId) {
    typeToSelect = healthMetricsStore.metricTypes.find((t) => t.id === urlTypeId)
  }
  if (!typeToSelect) {
    typeToSelect = healthMetricsStore.metricTypes[0]
  }

  if (typeToSelect) {
    selectedType.value = typeToSelect
    updateUrl()
    await Promise.all([loadMetrics(), loadTrend()])
  }
})
</script>

<template>
  <div class="health-metrics-view">
    <ConfirmDialog />
    <div class="page-header">
      <h1>Показники здоров'я</h1>
      <Button label="Новий показник" icon="pi pi-plus" @click="modalVisible = true" />
    </div>

    <!-- Metric type filter buttons -->
    <div class="type-filters">
      <Button
        v-for="type in healthMetricsStore.metricTypes"
        :key="type.id"
        :label="type.name"
        :severity="selectedType?.id === type.id ? undefined : 'secondary'"
        :outlined="selectedType?.id !== type.id"
        size="small"
        @click="selectType(type)"
      />
      <span v-if="healthMetricsStore.metricTypes.length === 0" class="empty-hint">
        Типи показників не створено. Додайте їх у Довідниках.
      </span>
    </div>

    <!-- Chart -->
    <div v-if="selectedType && trendData.length > 0" class="chart-section">
      <MetricChart :metricType="selectedType!" :dataPoints="trendData" />
    </div>
    <div v-else-if="selectedType && !trendLoading" class="chart-placeholder">
      <p>Немає даних для побудови графіка</p>
    </div>

    <!-- Data table -->
    <div v-if="selectedType" class="table-section">
      <DataTable
        :value="healthMetricsStore.healthMetrics"
        :loading="healthMetricsStore.loading"
        :lazy="true"
        :paginator="true"
        :rows="pageSize"
        :totalRecords="healthMetricsStore.total"
        :rowsPerPageOptions="[10, 20, 50]"
        @page="onPage"
        stripedRows
        scrollable
        class="metrics-table"
      >
        <template #empty>Показників не знайдено</template>
        <Column field="date" header="Дата" style="width: 180px">
          <template #body="{ data }">{{ formatDateTime(data.date) }}</template>
        </Column>
        <Column header="Значення">
          <template #body="{ data }">
            <span v-if="!showSecondaryColumn">{{ data.value }}</span>
            <span v-else>{{ formatValue(data) }}</span>
          </template>
        </Column>
        <Column v-if="showSecondaryColumn" header="Діастолічний">
          <template #body="{ data }">{{ data.secondary_value ?? '-' }}</template>
        </Column>
        <Column header="Одиниця" style="width: 100px">
          <template #body="{ data }">{{ data.metric_type?.unit || selectedType?.unit || '-' }}</template>
        </Column>
        <Column field="notes" header="Примітки" headerClass="hide-on-mobile" bodyClass="hide-on-mobile">
          <template #body="{ data }">
            <span class="notes-text">{{ data.notes || '-' }}</span>
          </template>
        </Column>
        <Column header="Дії" style="width: 80px; text-align: center">
          <template #body="{ data }">
            <Button icon="pi pi-trash" text severity="danger" @click="confirmDelete(data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <HealthMetricModal
      v-model:visible="modalVisible"
      :preselectedType="selectedType"
      @saved="onModalSaved"
    />
  </div>
</template>

<style scoped>
.health-metrics-view {
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
.type-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  border: 1px solid var(--border-subtle);
}
.empty-hint {
  color: var(--text-muted);
  font-size: 0.875rem;
}
.chart-section {
  margin-bottom: 1.5rem;
}
.chart-placeholder {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.5rem;
  padding: 2rem;
  border: 1px solid var(--border-subtle);
  text-align: center;
  margin-bottom: 1.5rem;
}
.chart-placeholder p {
  color: var(--text-muted);
  margin: 0;
}
.table-section {
  margin-bottom: 1rem;
}
.notes-text {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}
</style>
