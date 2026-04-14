<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, isDemoMode } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'
import NotificationBell from '@/components/NotificationBell.vue'
import GlobalSearch from '@/components/GlobalSearch/GlobalSearch.vue'
import DemoBanner from '@/components/DemoBanner.vue'
import { useOnlineStatus } from '@/composables/useOnlineStatus'
import { useGlobalSearch } from '@/composables/useGlobalSearch'

const { isOnline } = useOnlineStatus()
const { visible: searchVisible, open: openSearch } = useGlobalSearch()

const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)

// Demo banner dismissal is in-memory only (US3.2). Reload restores it.
const demoBannerDismissed = ref(false)

router.afterEach(() => {
  sidebarOpen.value = false
})

async function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <header class="mobile-header">
      <button class="hamburger-btn" @click="sidebarOpen = !sidebarOpen">
        <i class="pi pi-bars" />
      </button>
      <span class="mobile-title">Aura</span>
      <button class="mobile-search-btn" @click="openSearch" title="Пошук">
        <i class="pi pi-search" />
      </button>
    </header>
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false" />
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <h2 class="sidebar-title">
        Aura
        <span v-if="isDemoMode" class="demo-badge" title="Демо-режим">DEMO</span>
      </h2>
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
        <RouterLink to="/lab-results" class="nav-link">
          <i class="pi pi-chart-bar" /> Аналізи
        </RouterLink>
        <RouterLink to="/health-metrics" class="nav-link">
          <i class="pi pi-heart" /> Показники
        </RouterLink>
        <RouterLink to="/calendar" class="nav-link">
          <i class="pi pi-calendar" /> Календар
        </RouterLink>
        <RouterLink to="/vaccinations" class="nav-link">
          <i class="pi pi-shield" /> Вакцинації
        </RouterLink>
        <RouterLink to="/references" class="nav-link">
          <i class="pi pi-book" /> Довідники
        </RouterLink>
        <RouterLink to="/weather" class="nav-link">
          <i class="pi pi-cloud" /> Погода
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-actions">
          <button class="search-btn" @click="openSearch" title="Пошук (Ctrl+K)">
            <i class="pi pi-search" />
          </button>
          <NotificationBell />
          <ThemeToggle />
        </div>
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
      <DemoBanner :visible="isDemoMode && !demoBannerDismissed" @dismiss="demoBannerDismissed = true" />
      <div v-if="!isOnline" class="offline-banner">
        <i class="pi pi-wifi" /> Немає з'єднання
      </div>
      <slot />
    </main>
    <GlobalSearch v-model:visible="searchVisible" />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}
.mobile-header {
  display: none;
}
.sidebar-overlay {
  display: none;
}
.sidebar {
  width: 240px;
  background: var(--bg-sidebar);
  color: var(--text-secondary);
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  transition: transform 0.3s ease;
}
.sidebar-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 2rem;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.demo-badge {
  background: #facc15;
  color: #1f2937;
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.125rem 0.4rem;
  border-radius: 2px;
  letter-spacing: 0.1em;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 2px;
  color: var(--text-muted);
  text-decoration: none;
  margin-bottom: 0.25rem;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.05em;
}
.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-link.router-link-active {
  background: var(--bg-active);
  color: var(--accent);
  border-right: 2px solid var(--accent);
}
.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
}
.sidebar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.search-btn {
  background: none;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background 0.2s;
}
.search-btn:hover {
  color: var(--accent);
  background: var(--bg-hover);
}
.profile-link {
  margin-bottom: 0.75rem;
}
.username {
  display: block;
  font-size: 0.875rem;
  color: var(--text-faint);
  margin-bottom: 0.5rem;
}
.logout-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  transition: color 0.2s;
}
.logout-btn:hover {
  color: var(--danger);
}
.main-content {
  flex: 1;
  padding: 2rem;
  background: var(--bg-main);
}

.offline-banner {
  background: var(--danger);
  color: #fff;
  text-align: center;
  padding: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* Tablet + Mobile */
@media (max-width: 1024px) {
  .app-layout {
    flex-direction: column;
  }
  .mobile-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--bg-sidebar);
    border-bottom: 1px solid var(--border-subtle);
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .hamburger-btn {
    background: none;
    border: none;
    color: var(--text-primary);
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0.5rem;
    min-height: 44px;
    min-width: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .mobile-title {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-primary);
    flex: 1;
  }
  .mobile-search-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1.1rem;
    cursor: pointer;
    padding: 0.5rem;
    min-height: 44px;
    min-width: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 200;
    transform: translateX(-100%);
  }
  .sidebar.open {
    transform: translateX(0);
  }
  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 150;
  }
  .main-content {
    padding: 1rem;
  }
  .nav-link {
    min-height: 44px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sidebar {
    transition: none;
  }
}
</style>
