import type { AxiosError } from 'axios'

export interface ApiErrorData {
  detail?: string
  message?: string
}

export type ApiError = AxiosError<ApiErrorData>

/**
 * Extract a human-readable error message from an unknown catch value.
 */
export function getErrorMessage(e: unknown, fallback: string): string {
  if (e && typeof e === 'object' && 'response' in e) {
    const axiosErr = e as ApiError
    return axiosErr.response?.data?.detail || fallback
  }
  if (e instanceof Error) {
    return e.message
  }
  return fallback
}
