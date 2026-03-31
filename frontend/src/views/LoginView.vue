<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
  background: #050505;
}
.login-card {
  background: #0c0c0c;
  padding: 2.5rem;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  width: 100%;
  max-width: 400px;
}
.login-card h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #fff;
  margin-bottom: 0.25rem;
}
.subtitle {
  color: #52525b;
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
  color: #52525b;
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
  color: #d4d4d8;
  transition: border-color 0.2s;
}
.field input:focus {
  outline: none;
  border-color: #22d3ee;
}
.error {
  color: #ef4444;
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
  background: #22d3ee;
}
.login-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
