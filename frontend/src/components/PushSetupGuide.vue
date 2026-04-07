<script setup lang="ts">
import { computed } from 'vue'

const device = computed<'ios' | 'android' | 'macos' | 'windows' | 'linux' | 'unknown'>(() => {
  const ua = navigator.userAgent
  if (/iPad|iPhone|iPod/.test(ua)) return 'ios'
  if (/Android/.test(ua)) return 'android'
  if (/Macintosh|Mac OS X/.test(ua)) return 'macos'
  if (/Windows/.test(ua)) return 'windows'
  if (/Linux/.test(ua)) return 'linux'
  return 'unknown'
})

const browser = computed<'chrome' | 'safari' | 'firefox' | 'edge' | 'other'>(() => {
  const ua = navigator.userAgent
  if (/Edg\//.test(ua)) return 'edge'
  if (/Chrome\//.test(ua) && !/Edg\//.test(ua)) return 'chrome'
  if (/Safari\//.test(ua) && !/Chrome\//.test(ua)) return 'safari'
  if (/Firefox\//.test(ua)) return 'firefox'
  return 'other'
})

const isStandalone = computed(() => window.matchMedia('(display-mode: standalone)').matches)

const deviceLabel = computed(() => ({
  ios: 'iPhone / iPad',
  android: 'Android',
  macos: 'macOS',
  windows: 'Windows',
  linux: 'Linux',
  unknown: 'Невідомий пристрій',
}[device.value]))

const browserLabel = computed(() => ({
  chrome: 'Chrome',
  safari: 'Safari',
  firefox: 'Firefox',
  edge: 'Edge',
  other: 'Браузер',
}[browser.value]))
</script>

<template>
  <div class="push-guide">
    <div class="guide-header">
      <i class="pi pi-info-circle" />
      <span>Налаштування для цього пристрою</span>
      <span class="device-badge">{{ deviceLabel }} · {{ browserLabel }}</span>
    </div>

    <!-- iOS Safari (not installed) -->
    <div v-if="device === 'ios' && !isStandalone" class="guide-steps">
      <p class="guide-note warning">Push-сповіщення на iOS працюють тільки з головного екрану.</p>
      <ol>
        <li>Відкрийте Aura в <strong>Safari</strong></li>
        <li>Натисніть <strong>Поділитися</strong> (іконка <i class="pi pi-share-alt" /> внизу)</li>
        <li>Оберіть <strong>«На Початковий екран»</strong></li>
        <li>Відкрийте Aura з іконки на головному екрані</li>
        <li>Увімкніть сповіщення в <strong>Профілі</strong></li>
      </ol>
      <p class="guide-note">Також перевірте: <strong>Налаштування → Aura → Сповіщення → Увімкнено</strong></p>
    </div>

    <!-- iOS installed PWA -->
    <div v-else-if="device === 'ios' && isStandalone" class="guide-steps">
      <p class="guide-note success">Aura встановлено як додаток. Push-сповіщення доступні.</p>
      <ol>
        <li>Увімкніть сповіщення перемикачем вище</li>
        <li>Дозвольте сповіщення у спливаючому вікні браузера</li>
      </ol>
      <p class="guide-note">Якщо не працює: <strong>Налаштування → Aura → Сповіщення</strong> — має бути увімкнено</p>
    </div>

    <!-- Android Chrome -->
    <div v-else-if="device === 'android'" class="guide-steps">
      <ol>
        <li>Увімкніть сповіщення перемикачем вище</li>
        <li>Дозвольте сповіщення у спливаючому вікні</li>
        <li v-if="!isStandalone">
          Для кращого досвіду: <strong>Меню (⋮) → Встановити додаток</strong>
        </li>
      </ol>
      <p class="guide-note">Якщо не працює: <strong>Налаштування → Додатки → {{ browserLabel }} → Сповіщення → Увімкнено</strong></p>
    </div>

    <!-- macOS -->
    <div v-else-if="device === 'macos'" class="guide-steps">
      <ol>
        <li>Увімкніть сповіщення <strong>перемикачем вище</strong></li>
        <li>У спливаючому вікні браузера натисніть <strong>«Дозволити»</strong></li>
        <li>Переконайтесь що сповіщення для {{ browserLabel }} увімкнено в системі:
          <strong>Системні налаштування → Сповіщення → {{ browserLabel }}</strong> — має бути увімкнено
        </li>
        <li>Перевірте, що режим <strong>«Не турбувати» / «Фокус»</strong> вимкнено</li>
      </ol>
      <p class="guide-note">
        Сповіщення приходять навіть коли вкладка закрита, якщо {{ browserLabel }} працює у фоні.
        Для тесту натисніть кнопку «Тестове push-сповіщення» на головній сторінці (потрібен TEST_MODE).
      </p>
    </div>

    <!-- Windows -->
    <div v-else-if="device === 'windows'" class="guide-steps">
      <ol>
        <li>Увімкніть сповіщення перемикачем вище</li>
        <li>Дозвольте сповіщення у спливаючому вікні браузера</li>
      </ol>
      <p class="guide-note">
        Якщо не працює: <strong>Параметри → Система → Сповіщення</strong> — {{ browserLabel }} має бути увімкнено.
        Також перевірте <strong>Фокус</strong> (режим «Не турбувати»).
      </p>
    </div>

    <!-- Linux / other -->
    <div v-else class="guide-steps">
      <ol>
        <li>Увімкніть сповіщення перемикачем вище</li>
        <li>Дозвольте сповіщення у спливаючому вікні браузера</li>
      </ol>
      <p class="guide-note">Перевірте системні налаштування сповіщень для {{ browserLabel }}.</p>
    </div>
  </div>
</template>

<style scoped>
.push-guide {
  margin-top: 0.75rem;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: hidden;
}
.guide-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: var(--bg-hover);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}
.guide-header i {
  color: var(--accent);
}
.device-badge {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--text-faint);
  background: var(--bg-card);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}
.guide-steps {
  padding: 0.75rem 1rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  line-height: 1.7;
}
.guide-steps ol {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}
.guide-steps li {
  margin-bottom: 0.25rem;
}
.guide-note {
  font-size: 0.75rem;
  color: var(--text-faint);
  margin: 0.5rem 0 0;
}
.guide-note.warning {
  color: var(--danger);
  font-weight: 500;
  font-size: 0.8125rem;
}
.guide-note.success {
  color: var(--success);
  font-weight: 500;
  font-size: 0.8125rem;
}
</style>
