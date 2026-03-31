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
      <h2 class="sidebar-title">Aura</h2>
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
        <RouterLink to="/profile" class="nav-link profile-link">
          <i class="pi pi-user" /> Профіль
        </RouterLink>
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
  background: #080808;
  color: #a1a1aa;
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
.sidebar-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 2rem;
  color: #fff;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 2px;
  color: #71717a;
  text-decoration: none;
  margin-bottom: 0.25rem;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.05em;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #d4d4d8;
}
.nav-link.router-link-active {
  background: rgba(34, 211, 238, 0.08);
  color: #22d3ee;
  border-right: 2px solid #22d3ee;
}
.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.profile-link {
  margin-bottom: 0.75rem;
}
.username {
  display: block;
  font-size: 0.875rem;
  color: #52525b;
  margin-bottom: 0.5rem;
}
.logout-btn {
  background: none;
  border: none;
  color: #71717a;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  transition: color 0.2s;
}
.logout-btn:hover {
  color: #ef4444;
}
.main-content {
  flex: 1;
  padding: 2rem;
  background: #0a0a0a;
}
</style>
