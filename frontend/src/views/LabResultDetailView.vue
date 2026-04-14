<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import { useConfirm } from 'primevue/useconfirm'
import AppConfirmDialog from '@/components/AppConfirmDialog.vue'
import { useLabResultsStore } from '@/stores/labResults'
import type { BiomarkerTrendPoint } from '@/api/labResults'
import BiomarkerChart from '@/components/BiomarkerChart.vue'
import { formatDate } from '@/utils/dateUtils'

const route = useRoute()
const router = useRouter()
const labResultsStore = useLabResultsStore()
const confirm = useConfirm()

const labResultId = Number(route.params.id)

const selectedBiomarker = ref<string | null>(null)
const trendData = ref<BiomarkerTrendPoint[]>([])
const trendLoading = ref(false)

async function handleDelete() {
  confirm.require({
    message: 'Ви впевнені, що хочете видалити цей аналіз?',
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await labResultsStore.remove(labResultId)
      router.push({ name: 'lab-results' })
    },
  })
}

async function loadBiomarkerTrend(biomarkerName: string) {
  selectedBiomarker.value = biomarkerName
  trendLoading.value = true
  try {
    trendData.value = await labResultsStore.fetchBiomarkerTrend(biomarkerName)
  } catch {
    trendData.value = []
  } finally {
    trendLoading.value = false
  }
}

onMounted(async () => {
  await labResultsStore.fetchOne(labResultId)
})
</script>

<template>
  <div class="lab-result-detail">
    <AppConfirmDialog />
    <div class="page-header">
      <h1>Деталі аналізу</h1>
      <div class="actions">
        <Button label="Редагувати" icon="pi pi-pencil" @click="router.push({ name: 'lab-result-edit', params: { id: labResultId } })" />
        <Button label="Видалити" icon="pi pi-trash" severity="danger" outlined @click="handleDelete" />
        <Button label="Назад" icon="pi pi-arrow-left" severity="secondary" text @click="router.push({ name: 'lab-results' })" />
      </div>
    </div>

    <div v-if="labResultsStore.loading" class="loading">Завантаження...</div>

    <div v-else-if="labResultsStore.currentItem" class="detail-card">
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">Дата</span>
          <span class="detail-value">{{ formatDate(labResultsStore.currentItem.date) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Візит</span>
          <span class="detail-value">
            <template v-if="labResultsStore.currentItem.visit_id">
              <RouterLink
                :to="{ name: 'visit-detail', params: { id: labResultsStore.currentItem.visit_id } }"
                class="detail-link"
              >
                {{ labResultsStore.currentItem.visit_date
                  ? formatDate(labResultsStore.currentItem.visit_date)
                  : `Візит #${labResultsStore.currentItem.visit_id}` }}
              </RouterLink>
            </template>
            <template v-else>-</template>
          </span>
        </div>
        <div v-if="labResultsStore.currentItem.notes" class="detail-item full-width">
          <span class="detail-label">Примітки</span>
          <span class="detail-value">{{ labResultsStore.currentItem.notes }}</span>
        </div>
      </div>

      <div class="entries-section">
        <h3>Показники</h3>
        <DataTable
          :value="labResultsStore.currentItem.entries"
          stripedRows
          class="entries-table"
        >
          <template #empty>Показників не знайдено</template>
          <Column field="biomarker_name" header="Біомаркер">
            <template #body="{ data }">
              <button class="biomarker-link" @click="loadBiomarkerTrend(data.biomarker_name)">
                {{ data.biomarker_name }}
              </button>
            </template>
          </Column>
          <Column field="value" header="Значення" style="width: 120px">
            <template #body="{ data }">
              <span :class="{ 'out-of-range': data.is_normal === false }">{{ data.value }}</span>
            </template>
          </Column>
          <Column field="unit" header="Одиниця" style="width: 100px" />
          <Column field="ref_min" header="Мін" style="width: 80px">
            <template #body="{ data }">{{ data.ref_min ?? '-' }}</template>
          </Column>
          <Column field="ref_max" header="Макс" style="width: 80px">
            <template #body="{ data }">{{ data.ref_max ?? '-' }}</template>
          </Column>
          <Column header="Норма" style="width: 140px; text-align: center">
            <template #body="{ data }">
              <Tag v-if="data.is_normal === true" value="Норма" severity="success" />
              <Tag v-else-if="data.is_normal === false" value="Поза нормою" severity="danger" />
              <span v-else class="no-range">&mdash;</span>
            </template>
          </Column>
        </DataTable>
      </div>

      <div v-if="selectedBiomarker" class="trend-section">
        <h3>Тренд: {{ selectedBiomarker }}</h3>
        <div v-if="trendLoading" class="loading">Завантаження графіку...</div>
        <BiomarkerChart
          v-else-if="trendData.length > 0"
          :biomarkerName="selectedBiomarker"
          :dataPoints="trendData"
        />
        <p v-else class="no-data">Недостатньо даних для побудови графіку</p>
      </div>

      <div class="timestamps">
        <span>Створено: {{ formatDate(labResultsStore.currentItem.created) }}</span>
        <span>Оновлено: {{ formatDate(labResultsStore.currentItem.updated) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lab-result-detail {
  max-width: 1000px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}
.actions {
  display: flex;
  gap: 0.5rem;
}
.loading {
  text-align: center;
  padding: 3rem;
  color: var(--text-faint);
}
.detail-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 2rem;
  border: 1px solid var(--border-subtle);
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.detail-item.full-width {
  grid-column: 1 / -1;
}
.detail-label {
  font-size: 0.8rem;
  color: var(--text-faint);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
.detail-value {
  font-size: 1rem;
  color: var(--text-primary);
}
.detail-link {
  color: #2563eb;
  text-decoration: none;
}
.detail-link:hover {
  text-decoration: underline;
}
.entries-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-subtle);
}
.entries-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}
.biomarker-link {
  background: none;
  border: none;
  color: #2563eb;
  cursor: pointer;
  font-size: inherit;
  padding: 0;
  text-decoration: none;
  font-family: inherit;
}
.biomarker-link:hover {
  text-decoration: underline;
}
.out-of-range {
  color: var(--danger);
  font-weight: 600;
  background: rgba(239, 68, 68, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}
.no-range {
  color: var(--text-faint);
}
.trend-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-subtle);
}
.trend-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}
.no-data {
  color: var(--text-faint);
  font-size: 0.875rem;
}
.timestamps {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  gap: 2rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .detail-item.full-width {
    grid-column: auto;
  }
  .entries-section {
    overflow-x: auto;
  }
  .timestamps {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
