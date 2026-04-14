// Centralized demo interception layer (FR-007, FR-008).
// Provides wrapWithDemo() that wraps an API call with a demo fallback.
// When isDemoMode is true, the demo handler runs synchronously;
// otherwise the real API call is forwarded.

import { isDemoMode } from '@/stores/auth'

/**
 * Wrap an async API call with a synchronous demo fallback.
 * In demo mode, `demoFn` is called and its result is returned as a resolved promise.
 * In live mode, `apiFn` is called directly.
 */
export function wrapWithDemo<TArgs extends unknown[], TResult>(
  apiFn: (...args: TArgs) => Promise<TResult>,
  demoFn: (...args: TArgs) => TResult,
): (...args: TArgs) => Promise<TResult> {
  return (...args: TArgs): Promise<TResult> => {
    if (isDemoMode.value) {
      return Promise.resolve(demoFn(...args))
    }
    return apiFn(...args)
  }
}

/**
 * Wrap an async void API call with a synchronous demo fallback.
 */
export function wrapVoidWithDemo<TArgs extends unknown[]>(
  apiFn: (...args: TArgs) => Promise<void>,
  demoFn: (...args: TArgs) => void,
): (...args: TArgs) => Promise<void> {
  return (...args: TArgs): Promise<void> => {
    if (isDemoMode.value) {
      demoFn(...args)
      return Promise.resolve()
    }
    return apiFn(...args)
  }
}
