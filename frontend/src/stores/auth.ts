import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { apiClient } from '@/api/client'

// Reactive demo flag re-exported here so every Pinia store can check it
// without dynamic-importing the lazy demo module (research.md R3).
// The real demo module owns the underlying ref and updates it via setDemoMode().
export const isDemoMode = ref(false)

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value || isDemoMode.value)

  async function login(username: string, password: string) {
    const response = await apiClient.post('/api/v1/auth/login', { username, password })
    accessToken.value = response.data.access_token
    refreshToken.value = response.data.refresh_token
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)
    await fetchUser()
  }

  async function fetchUser() {
    const response = await apiClient.get('/api/v1/auth/me')
    user.value = response.data
  }

  async function refresh() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const response = await apiClient.post('/api/v1/auth/refresh', null, {
      params: { token: refreshToken.value },
    })
    accessToken.value = response.data.access_token
    refreshToken.value = response.data.refresh_token
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    // FR-009: logout also exits demo mode. The demo module's clearDemoCache()
    // is called via deactivateDemo() if the module was loaded; otherwise we
    // clear the flag directly so reload doesn't restore demo state.
    if (isDemoMode.value) {
      isDemoMode.value = false
      localStorage.removeItem('medtracker_demo_mode')
      // Best-effort lazy import to also drop the in-memory cache; failure
      // is silent because the flag is already clear.
      import('@/modules/demo')
        .then(({ deactivateDemo }) => deactivateDemo())
        .catch(() => {})
    }
  }

  return { accessToken, refreshToken, user, isAuthenticated, login, fetchUser, refresh, logout }
})
