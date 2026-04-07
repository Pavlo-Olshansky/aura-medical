<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch {
    error.value = 'Невірне ім\'я користувача або пароль'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-theme-toggle">
      <ThemeToggle />
    </div>
    <div class="login-card">
      <h1>Aura</h1>
      <p class="subtitle">Вхід до системи</p>
      <form @submit.prevent="handleLogin">
        <div class="field">
          <label for="username">Ім'я користувача</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            autocomplete="username"
          />
        </div>
        <div class="field">
          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
          />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading" class="login-btn">
          {{ loading ? 'Вхід...' : 'Увійти' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--bg-body);
  position: relative;
}
.login-theme-toggle {
  position: absolute;
  top: 1rem;
  right: 1rem;
}
.login-card {
  background: var(--bg-card);
  padding: 2.5rem;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  width: 100%;
  max-width: 400px;
}
.login-card h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}
.subtitle {
  color: var(--text-faint);
  margin-bottom: 1.5rem;
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.field {
  margin-bottom: 1rem;
}
.field label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 500;
  margin-bottom: 0.375rem;
  color: var(--text-faint);
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
.field input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  font-size: 0.875rem;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-primary);
  transition: border-color 0.2s;
}
.field input:focus {
  outline: none;
  border-color: var(--accent);
}
.error {
  color: var(--danger);
  font-size: 0.8125rem;
  margin-bottom: 0.75rem;
}
.login-btn {
  width: 100%;
  padding: 0.875rem;
  background: #fff;
  color: #000;
  border: none;
  border-radius: 2px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  cursor: pointer;
  transition: background 0.2s;
}
.login-btn:hover {
  background: var(--accent);
}
.login-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
