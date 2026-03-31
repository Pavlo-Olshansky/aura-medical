<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import { useReferencesStore } from '@/stores/references'
import type { ReferenceResource } from '@/api/references'
import type { Reference } from '@/types'

const referencesStore = useReferencesStore()
const confirm = useConfirm()

interface TabConfig {
  label: string
  resource: ReferenceResource
}

const tabs: TabConfig[] = [
  { label: 'Позиції', resource: 'positions' },
  { label: 'Процедури', resource: 'procedures' },
  { label: 'Клініки', resource: 'clinics' },
  { label: 'Міста', resource: 'cities' },
]

const editingRows = ref<Record<string, Record<number, { name: string }>>>({
  positions: {},
  procedures: {},
  clinics: {},
  cities: {},
})

const newItemName = ref<Record<string, string>>({
  positions: '',
  procedures: '',
  clinics: '',
  cities: '',
})

function getItems(resource: ReferenceResource): Reference[] {
  return referencesStore.getList(resource)
}

function startEdit(resource: ReferenceResource, item: Reference) {
  const rows = editingRows.value[resource]
  if (rows) rows[item.id] = { name: item.name }
}

function cancelEdit(resource: ReferenceResource, id: number) {
  const rows = editingRows.value[resource]
  if (rows) delete rows[id]
}

function isEditing(resource: ReferenceResource, id: number): boolean {
  const rows = editingRows.value[resource]
  return rows ? id in rows : false
}

function getEditName(resource: ReferenceResource, id: number): { name: string } {
  return editingRows.value[resource]?.[id] ?? { name: '' }
}

async function saveEdit(resource: ReferenceResource, id: number) {
  const editData = editingRows.value[resource]?.[id]
  if (!editData || !editData.name.trim()) return

  try {
    await referencesStore.editResource(resource, id, editData.name.trim())
    const rows = editingRows.value[resource]
    if (rows) delete rows[id]
  } catch {
    // error is handled in the store
  }
}

async function addItem(resource: ReferenceResource) {
  const name = newItemName.value[resource]?.trim()
  if (!name) return

  try {
    await referencesStore.addResource(resource, name)
    newItemName.value[resource] = ''
  } catch {
    // error is handled in the store
  }
}

function confirmDelete(resource: ReferenceResource, item: Reference) {
  confirm.require({
    message: `Ви впевнені, що хочете видалити "${item.name}"?`,
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await referencesStore.removeResource(resource, item.id)
    },
  })
}

onMounted(async () => {
  await referencesStore.fetchAll()
})
</script>

<template>
  <div class="references-view">
    <ConfirmDialog />
    <h1>Довідники</h1>

    <TabView>
      <TabPanel v-for="tab in tabs" :key="tab.resource" :value="tab.resource" :header="tab.label">
        <div class="add-row">
          <InputText
            v-model="newItemName[tab.resource]"
            :placeholder="`Нова назва...`"
            @keyup.enter="addItem(tab.resource)"
          />
          <Button
            label="Додати"
            icon="pi pi-plus"
            :disabled="!newItemName[tab.resource]?.trim()"
            @click="addItem(tab.resource)"
          />
        </div>

        <DataTable
          :value="getItems(tab.resource)"
          :loading="referencesStore.loading"
          stripedRows
        >
          <template #empty>Записів не знайдено</template>
          <Column field="name" header="Назва" style="min-width: 300px">
            <template #body="{ data }">
              <div v-if="isEditing(tab.resource, data.id)" class="edit-cell">
                <InputText
                  v-model="getEditName(tab.resource, data.id).name"
                  @keyup.enter="saveEdit(tab.resource, data.id)"
                  @keyup.escape="cancelEdit(tab.resource, data.id)"
                />
                <Button icon="pi pi-check" text severity="success" @click="saveEdit(tab.resource, data.id)" />
                <Button icon="pi pi-times" text severity="secondary" @click="cancelEdit(tab.resource, data.id)" />
              </div>
              <span v-else>{{ data.name }}</span>
            </template>
          </Column>
          <Column header="Дії" style="width: 150px; text-align: center">
            <template #body="{ data }">
              <div v-if="!isEditing(tab.resource, data.id)" class="action-buttons">
                <Button icon="pi pi-pencil" text severity="info" @click="startEdit(tab.resource, data)" />
                <Button icon="pi pi-trash" text severity="danger" @click="confirmDelete(tab.resource, data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>
    </TabView>
  </div>
</template>

<style scoped>
.references-view {
  max-width: 800px;
}
.references-view h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e4e4e7;
  margin-bottom: 1.5rem;
}
.add-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  align-items: center;
}
.add-row .p-inputtext {
  flex: 1;
}
.edit-cell {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.edit-cell .p-inputtext {
  flex: 1;
}
.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}
</style>
