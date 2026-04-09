import { onMounted, onUnmounted, type Ref } from 'vue'

const OVERLAY_SELECTORS = [
  '.p-select-overlay',
  '.p-dropdown-panel',
  '.p-datepicker-panel',
  '.p-datepicker-overlay',
  '.p-autocomplete-overlay',
  '.p-confirmdialog',
].join(', ')

export function useEnterSubmit(submitFn: () => void, active?: Ref<boolean>) {
  function handleKeydown(e: KeyboardEvent) {
    if (e.key !== 'Enter') return
    if (active && !active.value) return

    const target = e.target as HTMLElement
    if (target.tagName === 'TEXTAREA') return
    if (target.tagName === 'BUTTON' || target.closest('button')) return
    if (document.querySelector(OVERLAY_SELECTORS)) return

    e.preventDefault()
    submitFn()
  }

  onMounted(() => document.addEventListener('keydown', handleKeydown))
  onUnmounted(() => document.removeEventListener('keydown', handleKeydown))
}
