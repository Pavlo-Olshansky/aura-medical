// Generic in-memory CRUD helpers used by every store's demo branch.
// Mutations live only for the page lifetime (FR-013, FR-014, US4.6).
// Stores call these inside their `if (isDemoMode.value) { ... }` blocks
// and emit the appropriate Ukrainian toast themselves.

export function demoCreate<T extends { id: number }>(
  collection: T[],
  record: Omit<T, 'id'>,
): T {
  const nextId = collection.length === 0 ? 1 : Math.max(...collection.map((r) => r.id)) + 1
  const created = { ...(record as object), id: nextId } as T
  collection.push(created)
  return created
}

export function demoUpdate<T extends { id: number }>(
  collection: T[],
  id: number,
  patch: Partial<T>,
): T | undefined {
  const idx = collection.findIndex((r) => r.id === id)
  if (idx === -1) return undefined
  collection[idx] = { ...collection[idx], ...patch } as T
  return collection[idx]
}

export function demoDelete<T extends { id: number }>(collection: T[], id: number): boolean {
  const idx = collection.findIndex((r) => r.id === id)
  if (idx === -1) return false
  collection.splice(idx, 1)
  return true
}
