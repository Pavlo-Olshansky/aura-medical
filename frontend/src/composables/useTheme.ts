import { ref, watch, onMounted } from 'vue'

export type ThemeMode = 'dark' | 'light' | 'system'

const STORAGE_KEY = 'theme'

function readStorage(): ThemeMode {
  try {
    const val = localStorage.getItem(STORAGE_KEY)
    if (val === 'dark' || val === 'light' || val === 'system') return val
  } catch {
    // localStorage unavailable
  }
  return 'dark'
}

const mode = ref<ThemeMode>(readStorage())

function getEffectiveTheme(m: ThemeMode): 'dark' | 'light' {
  if (m === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return m
}

function applyTheme(m: ThemeMode) {
  const effective = getEffectiveTheme(m)
  const el = document.documentElement
  el.classList.remove('dark', 'light')
  el.classList.add(effective)
}

export function useTheme() {
  onMounted(() => {
    applyTheme(mode.value)

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (mode.value === 'system') applyTheme('system')
    })
  })

  watch(mode, (val) => {
    try {
      localStorage.setItem(STORAGE_KEY, val)
    } catch {
      // localStorage unavailable
    }
    applyTheme(val)
  })

  function cycleTheme() {
    const order: ThemeMode[] = ['dark', 'light', 'system']
    const idx = order.indexOf(mode.value)
    mode.value = order[(idx + 1) % order.length] as ThemeMode
  }

  return { mode, cycleTheme, applyTheme }
}
