<script setup lang="ts">
import type { WeatherSummary } from '@/types/weather'

defineProps<{
  weather: WeatherSummary
}>()
</script>

<template>
  <div class="weather-banner">
    <div class="banner-main">
      <img
        :src="`https://openweathermap.org/img/wn/${weather.condition_icon}@2x.png`"
        :alt="weather.condition_description"
        class="weather-icon-img"
      />
      <div class="banner-temp">
        <span class="temp-value">{{ Math.round(weather.temperature) }}°C</span>
        <span class="temp-feels">відчувається як {{ Math.round(weather.feels_like) }}°</span>
      </div>
      <div class="banner-condition">{{ weather.condition_description }}</div>
    </div>
    <div class="banner-details">
      <div class="detail-item">
        <i class="pi pi-sun" />
        <span>Вологість: {{ weather.humidity }}%</span>
      </div>
      <div class="detail-item">
        <i class="pi pi-arrows-v" />
        <span>Тиск: {{ weather.pressure }} гПа</span>
      </div>
      <div class="detail-item">
        <i class="pi pi-send" />
        <span>Вітер: {{ weather.wind_speed }} м/с</span>
      </div>
      <div class="detail-item">
        <i class="pi pi-cloud" />
        <span>Хмарність: {{ weather.clouds }}%</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.weather-banner {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.banner-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.weather-icon-img {
  width: 64px;
  height: 64px;
}
.temp-value {
  font-size: 2.5rem;
  font-weight: 300;
  color: var(--text-primary);
  line-height: 1;
}
.temp-feels {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}
.banner-condition {
  font-size: 1rem;
  color: var(--text-secondary);
  text-transform: capitalize;
}
.banner-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}
.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}
.detail-item i {
  color: var(--text-faint);
  font-size: 0.875rem;
}
</style>
