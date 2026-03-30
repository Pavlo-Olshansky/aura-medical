<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

async function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <h2 class="sidebar-title">MedTracker</h2>
      <nav>
        <RouterLink to="/" class="nav-link">
          <i class="pi pi-home" /> Головна
        </RouterLink>
        <RouterLink to="/visits" class="nav-link">
          <i class="pi pi-calendar" /> Візити
        </RouterLink>
        <RouterLink to="/treatments" class="nav-link">
          <i class="pi pi-heart" /> Лікування
        </RouterLink>
        <RouterLink to="/references" class="nav-link">
          <i class="pi pi-book" /> Довідники
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <span class="username">{{ auth.user?.username }}</span>
        <button class="logout-btn" @click="handleLogout">
          <i class="pi pi-sign-out" /> Вийти
        </button>
      </div>
    </aside>
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 240px;
  background: #1e293b;
  color: #e2e8f0;
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
}
.sidebar-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #fff;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: #cbd5e1;
  text-decoration: none;
  margin-bottom: 0.25rem;
  transition: background 0.15s;
}
.nav-link:hover,
.nav-link.router-link-active {
  background: #334155;
  color: #fff;
}
.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #334155;
}
.username {
  display: block;
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 0.5rem;
}
.logout-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
}
.main-content {
  flex: 1;
  padding: 2rem;
  background: #f8fafc;
}
</style>
