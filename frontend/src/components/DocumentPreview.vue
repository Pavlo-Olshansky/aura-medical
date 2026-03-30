<script setup lang="ts">
import { computed, ref, watch, onUnmounted } from 'vue'
import { apiClient } from '@/api/client'

const props = defineProps<{
  documentPath: string | null
  visitId: number
}>()

const blobUrl = ref<string | null>(null)
const loading = ref(false)
const error = ref(false)

const isImage = computed(() => {
  if (!props.documentPath) return false
  const ext = props.documentPath.split('.').pop()?.toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '')
})

const fileName = computed(() => {
  if (!props.documentPath) return ''
  return props.documentPath.split('/').pop() || props.documentPath
})

async function fetchDocument() {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
    blobUrl.value = null
  }
  error.value = false

  if (!props.documentPath) return

  loading.value = true
  try {
    const response = await apiClient.get(`/api/visits/${props.visitId}/document`, {
      responseType: 'blob',
    })
    blobUrl.value = URL.createObjectURL(response.data)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

watch(() => [props.visitId, props.documentPath], fetchDocument, { immediate: true })

onUnmounted(() => {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
  }
})
</script>

<template>
  <div v-if="documentPath" class="document-preview">
    <p v-if="loading" class="loading">Завантаження документа...</p>
    <p v-else-if="error" class="error">Не вдалося завантажити документ</p>
    <template v-else-if="blobUrl">
      <img
        v-if="isImage"
        :src="blobUrl"
        :alt="fileName"
        class="preview-image"
      />
      <a v-else :href="blobUrl" :download="fileName" class="download-link">
        <i class="pi pi-download" />
        {{ fileName }}
      </a>
    </template>
  </div>
  <p v-else class="no-document">Документ не прикріплено</p>
</template>

<style scoped>
.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}
.download-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #2563eb;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border: 1px solid #2563eb;
  border-radius: 0.375rem;
}
.no-document {
  color: #94a3b8;
  font-style: italic;
}
.loading {
  color: #64748b;
}
.error {
  color: #dc2626;
}
</style>
