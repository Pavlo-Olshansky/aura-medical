import { ref, onMounted, onUnmounted } from 'vue'

const visible = ref(false)

export function useGlobalSearch() {
  function open() {
    visible.value = true
  }

  function close() {
    visible.value = false
  }

  function handleKeydown(e: KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      visible.value = true
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })

  return { visible, open, close }
}
