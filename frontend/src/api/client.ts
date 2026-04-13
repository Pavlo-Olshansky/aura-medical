import axios from 'axios'
import { isDemoMode } from '@/stores/auth'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    // Defensive: in demo mode no requests should be made, but if one slips
    // through we MUST NOT trigger token-refresh or redirect-to-login (FR-006).
    if (isDemoMode.value) {
      return Promise.reject(error)
    }
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${apiClient.defaults.baseURL}/api/v1/auth/refresh`,
            null,
            { params: { token: refreshToken } },
          )
          const newAccessToken = response.data.access_token
          localStorage.setItem('access_token', newAccessToken)
          if (response.data.refresh_token) {
            localStorage.setItem('refresh_token', response.data.refresh_token)
          }
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return apiClient(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)
