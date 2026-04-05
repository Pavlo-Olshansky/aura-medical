<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getWeatherDetail } from '@/api/weather'
import type { WeatherDetail } from '@/types/weather'
import WeatherCurrentBanner from '@/components/weather/WeatherCurrentBanner.vue'
import WeatherUVSection from '@/components/weather/WeatherUVSection.vue'
import WeatherCircadianSection from '@/components/weather/WeatherCircadianSection.vue'
import WeatherAirQualitySection from '@/components/weather/WeatherAirQualitySection.vue'
import WeatherStormSection from '@/components/weather/WeatherStormSection.vue'

const loading = ref(true)
const data = ref<WeatherDetail | null>(null)
const error = ref(false)

onMounted(async () => {
  try {
    data.value = await getWeatherDetail()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="weather-page">
    <h1>Погода</h1>
    <p v-if="data" class="city-subtitle">{{ data.city }}</p>

    <div v-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner" /> Завантаження...
    </div>

    <div v-else-if="error" class="error-state">
      Не вдалося завантажити дані про погоду
    </div>

    <template v-else-if="data">
      <WeatherCurrentBanner v-if="data.weather" :weather="data.weather" />

      <div class="sections-grid">
        <WeatherUVSection v-if="data.uv" :data="data.uv" />
        <WeatherCircadianSection v-if="data.circadian" :data="data.circadian" />
        <WeatherAirQualitySection v-if="data.air_quality" :data="data.air_quality" />
        <WeatherStormSection v-if="data.magnetic_storm" :data="data.magnetic_storm" />
      </div>

      <div v-if="!data.uv && !data.circadian && !data.air_quality && !data.magnetic_storm" class="empty-state">
        Детальні дані недоступні
      </div>
    </template>
  </div>
</template>

<style scoped>
.weather-page {
  max-width: 1100px;
}
.weather-page h1 {
  font-size: 1.5rem;
  font-weight: 300;
  color: #e4e4e7;
  margin-bottom: 0.25rem;
  letter-spacing: 0.02em;
}
.city-subtitle {
  font-size: 0.875rem;
  color: #52525b;
  margin-bottom: 1.5rem;
}
.sections-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
.loading-state,
.error-state,
.empty-state {
  color: #52525b;
  font-size: 0.875rem;
  padding: 2rem;
  text-align: center;
}
.loading-state i {
  margin-right: 0.5rem;
}
.error-state {
  color: #ef4444;
}

@media (max-width: 768px) {
  .sections-grid {
    grid-template-columns: 1fr;
  }
}
</style>
