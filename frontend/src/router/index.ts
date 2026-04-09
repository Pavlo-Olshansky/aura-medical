import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/visits',
      name: 'visits',
      component: () => import('@/views/VisitsListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/visits/new',
      name: 'visit-create',
      component: () => import('@/views/VisitFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/visits/:id',
      name: 'visit-detail',
      component: () => import('@/views/VisitDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/visits/:id/edit',
      name: 'visit-edit',
      component: () => import('@/views/VisitFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/treatments',
      name: 'treatments',
      component: () => import('@/views/TreatmentsListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/treatments/new',
      name: 'treatment-create',
      component: () => import('@/views/TreatmentFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/treatments/:id/edit',
      name: 'treatment-edit',
      component: () => import('@/views/TreatmentFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/lab-results',
      name: 'lab-results',
      component: () => import('@/views/LabResultsListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/lab-results/new',
      name: 'lab-result-create',
      component: () => import('@/views/LabResultFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/lab-results/:id',
      name: 'lab-result-detail',
      component: () => import('@/views/LabResultDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/lab-results/:id/edit',
      name: 'lab-result-edit',
      component: () => import('@/views/LabResultFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/timeline',
      redirect: '/calendar',
    },
    {
      path: '/vaccinations',
      name: 'vaccinations',
      component: () => import('@/views/VaccinationsListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/vaccinations/new',
      name: 'vaccination-create',
      component: () => import('@/views/VaccinationFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/vaccinations/:id/edit',
      name: 'vaccination-edit',
      component: () => import('@/views/VaccinationFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/health-metrics',
      name: 'health-metrics',
      component: () => import('@/views/HealthMetricsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/references',
      name: 'references',
      component: () => import('@/views/ReferencesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/weather',
      name: 'weather',
      component: () => import('@/views/WeatherView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth !== false && !token) {
    return { name: 'login' }
  }
  if (to.name === 'login' && token) {
    return { name: 'dashboard' }
  }
})

export default router
