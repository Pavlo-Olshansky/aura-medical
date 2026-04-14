<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import AppConfirmDialog from '@/components/AppConfirmDialog.vue'
import ReferenceTable from '@/components/references/ReferenceTable.vue'
import MetricTypesPanel from '@/components/references/MetricTypesPanel.vue'
import BiomarkerPanel from '@/components/references/BiomarkerPanel.vue'
import { useReferencesStore } from '@/stores/references'
import type { ReferenceResource } from '@/api/references'
import type { Reference } from '@/types'

const referencesStore = useReferencesStore()
const activeTab = ref<string>()

onMounted(() => {
  nextTick(() => {
    activeTab.value = 'positions'
  })
  referencesStore.fetchAll()
})

// ─── Simple reference tabs ───
interface TabConfig {
  label: string
  resource: ReferenceResource
  placeholder: string
}

const tabs: TabConfig[] = [
  { label: 'Позиції', resource: 'positions', placeholder: 'Нова назва...' },
  { label: 'Процедури', resource: 'procedures', placeholder: 'Нова назва...' },
  { label: 'Клініки', resource: 'clinics', placeholder: 'Нова назва...' },
  { label: 'Міста', resource: 'cities', placeholder: 'Нова назва...' },
]

function getItems(resource: ReferenceResource): Reference[] {
  return referencesStore.getList(resource)
}

async function handleCreate(resource: ReferenceResource, name: string) {
  try {
    await referencesStore.addResource(resource, name)
  } catch {
    // error is handled in the store
  }
}

async function handleUpdate(resource: ReferenceResource, id: number, name: string) {
  try {
    await referencesStore.editResource(resource, id, name)
  } catch {
    // error is handled in the store
  }
}

async function handleDelete(resource: ReferenceResource, id: number) {
  await referencesStore.removeResource(resource, id)
}
</script>

<template>
  <div class="references-view">
    <AppConfirmDialog />
    <h1>Довідники</h1>

    <TabView v-model:value="activeTab">
      <!-- Simple reference tabs -->
      <TabPanel v-for="tab in tabs" :key="tab.resource" :value="tab.resource" :header="tab.label">
        <ReferenceTable
          :items="getItems(tab.resource)"
          :title="tab.label"
          :placeholder="tab.placeholder"
          :loading="referencesStore.loading"
          @create="(name) => handleCreate(tab.resource, name)"
          @update="(id, name) => handleUpdate(tab.resource, id, name)"
          @delete="(id) => handleDelete(tab.resource, id)"
        />
      </TabPanel>

      <!-- Metric Types tab -->
      <TabPanel value="metric-types" header="Типи показників">
        <MetricTypesPanel />
      </TabPanel>

      <!-- Biomarker References tab -->
      <TabPanel value="biomarker-refs" header="Біомаркери">
        <BiomarkerPanel />
      </TabPanel>
    </TabView>
  </div>
</template>

<style scoped>
.references-view {
  max-width: 1100px;
}
.references-view h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}
</style>
