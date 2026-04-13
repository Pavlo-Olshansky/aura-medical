// Module-level memoization for demo data generators.
// Generators run once per page load (FR-014). User mutations persist within
// the page lifetime because every store reads the same array reference;
// reload clears this Map and regenerates from the day-seeded RNG.

const cache = new Map<string, unknown>()

export function getOrCreate<T>(key: string, factory: () => T): T {
  if (!cache.has(key)) {
    cache.set(key, factory())
  }
  return cache.get(key) as T
}

export function clearDemoCache(): void {
  cache.clear()
}
