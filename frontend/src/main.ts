import './assets/main.css'
import 'primeicons/primeicons.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import Aura from '@primevue/themes/aura'

import Tooltip from 'primevue/tooltip'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark',
    },
  },
  locale: {
    startsWith: 'Починається з',
    contains: 'Містить',
    notContains: 'Не містить',
    endsWith: 'Закінчується на',
    equals: 'Дорівнює',
    notEquals: 'Не дорівнює',
    noFilter: 'Без фільтра',
    lt: 'Менше ніж',
    lte: 'Менше або дорівнює',
    gt: 'Більше ніж',
    gte: 'Більше або дорівнює',
    dateIs: 'Дата дорівнює',
    dateIsNot: 'Дата не дорівнює',
    dateBefore: 'Дата до',
    dateAfter: 'Дата після',
    clear: 'Очистити',
    apply: 'Застосувати',
    matchAll: 'Відповідає всім',
    matchAny: 'Відповідає будь-якому',
    addRule: 'Додати правило',
    removeRule: 'Видалити правило',
    accept: 'Так',
    reject: 'Ні',
    choose: 'Обрати',
    upload: 'Завантажити',
    cancel: 'Скасувати',
    dayNames: ['Неділя', 'Понеділок', 'Вівторок', 'Середа', 'Четвер', "П'ятниця", 'Субота'],
    dayNamesShort: ['Нед', 'Пон', 'Вів', 'Сер', 'Чет', "П'ят", 'Суб'],
    dayNamesMin: ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
    monthNames: [
      'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
      'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень',
    ],
    monthNamesShort: [
      'Січ', 'Лют', 'Бер', 'Кві', 'Тра', 'Чер',
      'Лип', 'Сер', 'Вер', 'Жов', 'Лис', 'Гру',
    ],
    today: 'Сьогодні',
    weekHeader: 'Тж',
    firstDayOfWeek: 1,
    dateFormat: 'dd.mm.yy',
    weak: 'Слабкий',
    medium: 'Середній',
    strong: 'Сильний',
    passwordPrompt: 'Введіть пароль',
    emptyFilterMessage: 'Результатів не знайдено',
    emptyMessage: 'Немає даних',
    aria: {
      trueLabel: 'Так',
      falseLabel: 'Ні',
      nullLabel: 'Не обрано',
      star: '1 зірка',
      stars: '{star} зірок',
      selectAll: 'Обрати всі',
      unselectAll: 'Скасувати вибір',
      close: 'Закрити',
      previous: 'Попередній',
      next: 'Наступний',
      navigation: 'Навігація',
      scrollTop: 'Прокрутити вгору',
      moveTop: 'Перемістити вгору',
      moveUp: 'Перемістити вище',
      moveDown: 'Перемістити нижче',
      moveBottom: 'Перемістити вниз',
      moveToTarget: 'Перемістити до цілі',
      moveToSource: 'Перемістити до джерела',
      moveAllToTarget: 'Перемістити все до цілі',
      moveAllToSource: 'Перемістити все до джерела',
      pageLabel: 'Сторінка {page}',
      firstPageLabel: 'Перша сторінка',
      lastPageLabel: 'Остання сторінка',
      nextPageLabel: 'Наступна сторінка',
      prevPageLabel: 'Попередня сторінка',
      rowsPerPageLabel: 'Рядків на сторінці',
    },
  },
})

app.use(ConfirmationService)
app.use(ToastService)

app.directive('tooltip', Tooltip)

// If the user previously activated demo mode, restore the flag + fake user
// AND register the demo accessors BEFORE mounting (FR-003, US1.4). This
// must be awaited because components mount synchronously after .mount()
// and immediately start polling stores (e.g. NotificationBell) — without
// the await, isDemoMode would still be false and the polling would hit
// the real backend with no token, producing 401s.
async function bootstrap() {
  if (localStorage.getItem('medtracker_demo_mode') === 'true') {
    const { restoreDemoIfPersisted } = await import('@/modules/demo')
    restoreDemoIfPersisted()
  }
  app.mount('#app')
}

bootstrap()
