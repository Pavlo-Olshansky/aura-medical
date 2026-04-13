// Seeded RNG used by every demo data generator so the dataset is stable
// within a calendar day (FR-010). Seed rotates each midnight so the demo
// data feels alive without any time-travel logic.

export function mulberry32(seed: number): () => number {
  let t = seed >>> 0
  return function () {
    t = (t + 0x6d2b79f5) >>> 0
    let x = t
    x = Math.imul(x ^ (x >>> 15), x | 1)
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61)
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296
  }
}

export function dailySeed(): number {
  return Math.floor(Date.now() / 86_400_000)
}

export function pick<T>(rng: () => number, items: readonly T[]): T {
  return items[Math.floor(rng() * items.length)] as T
}

export function intBetween(rng: () => number, min: number, max: number): number {
  return Math.floor(rng() * (max - min + 1)) + min
}

export function floatBetween(rng: () => number, min: number, max: number, decimals = 1): number {
  const value = rng() * (max - min) + min
  const factor = 10 ** decimals
  return Math.round(value * factor) / factor
}
