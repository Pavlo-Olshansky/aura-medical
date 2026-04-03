<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import { useVisitsStore } from '@/stores/visits'
import DocumentPreview from '@/components/DocumentPreview.vue'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import { formatDate } from '@/utils/dateUtils'

const route = useRoute()
const router = useRouter()
const visitsStore = useVisitsStore()
const confirm = useConfirm()

const visitId = Number(route.params.id)

async function handleDelete() {
  confirm.require({
    message: 'Ви впевнені, що хочете видалити цей візит?',
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await visitsStore.deleteVisit(visitId)
      router.push({ name: 'visits' })
    },
  })
}

onMounted(async () => {
  await visitsStore.fetchVisit(visitId)
})
</script>

<template>
  <div class="visit-detail">
    <ConfirmDialog />
    <div class="page-header">
      <h1>Деталі візиту</h1>
      <div class="actions">
        <Button label="Редагувати" icon="pi pi-pencil" @click="router.push({ name: 'visit-edit', params: { id: visitId } })" />
        <Button label="Видалити" icon="pi pi-trash" severity="danger" outlined @click="handleDelete" />
        <Button label="Назад" icon="pi pi-arrow-left" severity="secondary" text @click="router.push({ name: 'visits' })" />
      </div>
    </div>

    <div v-if="visitsStore.loading" class="loading">Завантаження...</div>

    <div v-else-if="visitsStore.currentVisit" class="detail-card">
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">Дата</span>
          <span class="detail-value">{{ formatDate(visitsStore.currentVisit.date) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Позиція лікаря</span>
          <span class="detail-value">{{ visitsStore.currentVisit.position?.name || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Лікар</span>
          <span class="detail-value">{{ visitsStore.currentVisit.doctor || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Процедура</span>
          <span class="detail-value">{{ visitsStore.currentVisit.procedure?.name || '-' }}</span>
        </div>
        <div v-if="visitsStore.currentVisit.procedure_details" class="detail-item full-width">
          <span class="detail-label">Деталі процедури</span>
          <span class="detail-value">{{ visitsStore.currentVisit.procedure_details }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Клініка</span>
          <span class="detail-value">{{ visitsStore.currentVisit.clinic?.name || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Місто</span>
          <span class="detail-value">{{ visitsStore.currentVisit.city?.name || '-' }}</span>
        </div>
        <div v-if="visitsStore.currentVisit.price != null" class="detail-item">
          <span class="detail-label">Вартість</span>
          <span class="detail-value">{{ visitsStore.currentVisit.price }} грн</span>
        </div>
        <div v-if="visitsStore.currentVisit.comment" class="detail-item full-width">
          <span class="detail-label">Коментар</span>
          <span class="detail-value">{{ visitsStore.currentVisit.comment }}</span>
        </div>
        <div v-if="visitsStore.currentVisit.link" class="detail-item full-width">
          <span class="detail-label">Посилання</span>
          <a :href="visitsStore.currentVisit.link" target="_blank" class="detail-link">
            {{ visitsStore.currentVisit.link }}
          </a>
        </div>
      </div>

      <div class="document-section">
        <h3>Документ</h3>
        <DocumentPreview
          :documentPath="visitsStore.currentVisit.document"
          :visitId="visitsStore.currentVisit.id"
        />
      </div>

      <div class="timestamps">
        <span>Створено: {{ formatDate(visitsStore.currentVisit.created) }}</span>
        <span>Оновлено: {{ formatDate(visitsStore.currentVisit.updated) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.visit-detail {
  max-width: 900px;
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
  color: #e4e4e7;
  margin: 0;
}
.actions {
  display: flex;
  gap: 0.5rem;
}
.loading {
  text-align: center;
  padding: 3rem;
  color: #52525b;
}
.detail-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
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
  color: #52525b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
.detail-value {
  font-size: 1rem;
  color: #d4d4d8;
}
.detail-link {
  color: #2563eb;
  text-decoration: none;
  word-break: break-all;
}
.detail-link:hover {
  text-decoration: underline;
}
.document-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.document-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #e4e4e7;
  margin-bottom: 1rem;
}
.timestamps {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 2rem;
  font-size: 0.8rem;
  color: #94a3b8;
}
</style>
