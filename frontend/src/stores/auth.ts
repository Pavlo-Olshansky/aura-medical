import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { apiClient } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(username: string, password: string) {
    const response = await apiClient.post('/api/auth/login', { username, password })
    accessToken.value = response.data.access_token
    refreshToken.value = response.data.refresh_token
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)
    await fetchUser()
  }

  async function fetchUser() {
    const response = await apiClient.get('/api/auth/me')
    user.value = response.data
  }

  async function refresh() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const response = await apiClient.post('/api/auth/refresh', null, {
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
  }

  return { accessToken, refreshToken, user, isAuthenticated, login, fetchUser, refresh, logout }
})
