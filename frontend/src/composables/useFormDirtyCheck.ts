import { ref, computed, watch, onUnmounted, type Ref, type ComputedRef } from 'vue'
import { useConfirm } from 'primevue/useconfirm'

export function useFormDirtyCheck(getFormValues: () => Record<string, unknown>) {
  const confirm = useConfirm()
  const snapshot = ref('')
  const isConfirmOpen = ref(false)

  function capture() {
    snapshot.value = JSON.stringify(getFormValues())
  }

  function reset() {
    snapshot.value = ''
  }

  const isDirty = computed(() => {
    if (!snapshot.value) return false
    return JSON.stringify(getFormValues()) !== snapshot.value
  })

  function confirmDiscard(): Promise<boolean> {
    if (!isDirty.value) return Promise.resolve(true)
    if (isConfirmOpen.value) return Promise.resolve(false)

    isConfirmOpen.value = true
    return new Promise((resolve) => {
      confirm.require({
        message: 'Відхилити незбережені зміни?',
        header: 'Незбережені зміни',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Відхилити',
        rejectLabel: 'Повернутися',
        acceptClass: 'p-button-danger',
        accept: () => {
          setTimeout(() => { isConfirmOpen.value = false }, 50)
          resolve(true)
        },
        reject: () => {
          setTimeout(() => { isConfirmOpen.value = false }, 50)
          resolve(false)
        },
      })
    })
  }

  function setupEscapeHandler(isVisible: Ref<boolean> | ComputedRef<boolean>, close: () => void) {
    const handler = (e: KeyboardEvent) => {
      if (e.key !== 'Escape' || !isVisible.value) return
      if (document.querySelector('.p-confirmdialog')) return
      confirmDiscard().then((ok) => { if (ok) close() })
    }

    watch(isVisible, (val) => {
      if (val) document.addEventListener('keydown', handler)
      else document.removeEventListener('keydown', handler)
    })

    onUnmounted(() => document.removeEventListener('keydown', handler))
  }

  return { isDirty, capture, reset, confirmDiscard, setupEscapeHandler }
}
