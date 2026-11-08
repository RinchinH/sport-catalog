<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface User {
  id: number
  username: string
  role: string
}

const mode = ref<'register' | 'login'>('register')
const username = ref('')
const password = ref('')
const token = ref(sessionStorage.getItem('sport_token') || '')
const user = ref<User | null>(null)
const error = ref('')
const message = ref('')
const loading = ref(false)

async function loadProfile() {
  if (!token.value) return
  const response = await axios.get<User>('/api/auth/me', {
    headers: { Authorization: `Bearer ${token.value}` }
  })
  user.value = response.data
}

function logout() {
  sessionStorage.removeItem('sport_token')
  token.value = ''
  user.value = null
  password.value = ''
}

async function submit() {
  loading.value = true
  error.value = ''
  message.value = ''

  try {
    if (mode.value === 'register') {
      await axios.post('/api/auth/register', {
        username: username.value,
        password: password.value
      })
      mode.value = 'login'
      password.value = ''
      message.value = 'Аккаунт создан. Теперь войдите.'
    } else {
      const response = await axios.post('/api/auth/login', {
        username: username.value,
        password: password.value
      })
      token.value = response.data.access_token
      sessionStorage.setItem('sport_token', token.value)
      await loadProfile()
    }
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const status = e.response?.status
      error.value = status === 409
        ? 'Такой логин уже занят'
        : status === 401
          ? 'Неверный логин или пароль'
          : 'Проверьте введённые данные или подключение к серверу'
    } else {
      error.value = 'Не удалось выполнить запрос'
    }
  } finally {
    loading.value = false
  }
}

function switchMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = ''
  message.value = ''
  password.value = ''
}

onMounted(async () => {
  try {
    await loadProfile()
  } catch {
    logout()
  }
})
</script>

<template>
  <main>
    <section class="card">
      <h1>СпортКаталог</h1>
      <p class="subtitle">Учебный проект на Vue + FastAPI</p>

      <template v-if="user">
        <h2>Личный кабинет</h2>
        <p>Вы успешно авторизовались.</p>
        <p><b>Логин:</b> {{ user.username }}</p>
        <p><b>Роль:</b> {{ user.role }}</p>
        <button @click="logout">Выйти</button>
      </template>

      <template v-else>
        <h2>{{ mode === 'register' ? 'Регистрация' : 'Вход' }}</h2>

        <form @submit.prevent="submit">
          <label for="username">Логин</label>
          <input
            id="username"
            v-model="username"
            autocomplete="username"
            minlength="3"
            maxlength="50"
            required
          />

          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="password"
            type="password"
            :autocomplete="mode === 'login'
              ? 'current-password'
              : 'new-password'"
            :minlength="mode === 'register' ? 8 : 1"
            required
          />

          <p v-if="error" class="error">{{ error }}</p>
          <p v-if="message" class="success">{{ message }}</p>

          <button type="submit" :disabled="loading">
            {{ loading ? 'Загрузка...' :
               mode === 'register' ? 'Зарегистрироваться' : 'Войти' }}
          </button>
        </form>

        <button class="link" type="button" @click="switchMode">
          {{ mode === 'register'
            ? 'Уже есть аккаунт? Войти'
            : 'Нет аккаунта? Зарегистрироваться' }}
        </button>
      </template>
    </section>
  </main>
</template>

<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #f2f5f8;
  color: #172331;
}
main {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}
.card {
  background: white;
  padding: 36px;
  width: min(100%, 430px);
  border-radius: 16px;
  box-shadow: 0 8px 28px #00000012;
}
h1 { margin-bottom: 4px; }
h2 { margin-top: 28px; }
.subtitle { color: #697685; font-size: 14px; }
label { display: block; margin-top: 18px; margin-bottom: 7px; }
input {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px solid #b8c4d0;
  border-radius: 8px;
  font-size: 16px;
}
button {
  width: 100%;
  padding: 12px;
  margin-top: 20px;
  color: white;
  background: #205ec7;
  border: 0;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}
button:disabled { opacity: .6; cursor: wait; }
button.link {
  background: transparent;
  color: #205ec7;
  margin-top: 8px;
}
.error { color: #c62828; }
.success { color: #16813a; }
</style>
