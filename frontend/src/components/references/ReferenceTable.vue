<script setup lang="ts">
import { ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useConfirm } from 'primevue/useconfirm'
import type { Reference } from '@/types'

defineProps<{
  items: Reference[]
  title: string
  placeholder: string
  loading: boolean
}>()

const emit = defineEmits<{
  create: [name: string]
  update: [id: number, name: string]
  delete: [id: number]
}>()

const confirm = useConfirm()

const newItemName = ref('')
const editingRows = ref<Record<number, { name: string }>>({})

function startEdit(item: Reference) {
  editingRows.value[item.id] = { name: item.name }
}

function cancelEdit(id: number) {
  delete editingRows.value[id]
}

function isEditing(id: number): boolean {
  return id in editingRows.value
}

function getEditName(id: number): { name: string } {
  return editingRows.value[id] ?? { name: '' }
}

function saveEdit(id: number) {
  const editData = editingRows.value[id]
  if (!editData || !editData.name.trim()) return
  emit('update', id, editData.name.trim())
  delete editingRows.value[id]
}

function addItem() {
  const name = newItemName.value.trim()
  if (!name) return
  emit('create', name)
  newItemName.value = ''
}

function confirmDelete(item: Reference) {
  confirm.require({
    message: `Ви впевнені, що хочете видалити "${item.name}"?`,
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: () => {
      emit('delete', item.id)
    },
  })
}
</script>

<template>
  <div class="add-row">
    <InputText
      v-model="newItemName"
      :placeholder="placeholder"
      @keyup.enter="addItem"
    />
    <Button
      label="Додати"
      icon="pi pi-plus"
      :disabled="!newItemName.trim()"
      @click="addItem"
    />
  </div>

  <DataTable
    :value="items"
    :loading="loading"
    stripedRows
  >
    <template #empty>Записів не знайдено</template>
    <Column field="name" header="Назва" style="min-width: 300px">
      <template #body="{ data }">
        <div v-if="isEditing(data.id)" class="edit-cell">
          <InputText
            v-model="getEditName(data.id).name"
            @keyup.enter="saveEdit(data.id)"
            @keyup.escape="cancelEdit(data.id)"
          />
          <Button icon="pi pi-check" text severity="success" @click="saveEdit(data.id)" />
          <Button icon="pi pi-times" text severity="secondary" @click="cancelEdit(data.id)" />
        </div>
        <span v-else>{{ data.name }}</span>
      </template>
    </Column>
    <Column header="Дії" style="width: 150px; text-align: center">
      <template #body="{ data }">
        <div v-if="!isEditing(data.id)" class="action-buttons">
          <Button icon="pi pi-pencil" text severity="info" @click="startEdit(data)" />
          <Button icon="pi pi-trash" text severity="danger" @click="confirmDelete(data)" />
        </div>
      </template>
    </Column>
  </DataTable>
</template>

<style scoped>
.add-row {
  display: flex;
  flex-wrap: wrap;
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
