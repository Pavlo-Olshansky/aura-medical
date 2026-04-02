/**
 * Format a date string for display in Ukrainian locale (dd.mm.yyyy).
 */
export function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

/**
 * Format a Date object to YYYY-MM-DD string for API requests.
 */
export function formatDateForApi(d: Date): string {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
