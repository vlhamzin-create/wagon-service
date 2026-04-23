import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface AuthUser {
  username: string
  roles: string[]
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  function setToken(t: string): void {
    token.value = t
    localStorage.setItem('access_token', t)
    _parseUser(t)
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  function _parseUser(t: string): void {
    try {
      const payload = JSON.parse(atob(t.split('.')[1]))
      user.value = { username: payload.username ?? payload.sub, roles: payload.roles ?? [] }
    } catch {
      user.value = null
    }
  }

  // Восстановление пользователя при загрузке страницы
  if (token.value) _parseUser(token.value)

  return { token, user, isAuthenticated, setToken, logout }
})
