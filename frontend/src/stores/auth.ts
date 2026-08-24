import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token') || null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = () => !!token.value

  function setAuth(newUser: User, newToken: string) {
    user.value = newUser
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function clearAuth() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  async function login(username: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const res = await authApi.login({ username, password })
      if (res.data.success && res.data.data) {
        setAuth(res.data.data.user, res.data.data.token)
        return true
      }
      error.value = res.data.error?.message || 'เข้าสู่ระบบไม่สำเร็จ'
      return false
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'เข้าสู่ระบบไม่สำเร็จ'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(data: { username: string; email: string; password: string }) {
    loading.value = true
    error.value = null
    try {
      const res = await authApi.register(data)
      if (res.data.success) return true
      error.value = res.data.error?.message || 'สมัครสมาชิกไม่สำเร็จ'
      return false
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'สมัครสมาชิกไม่สำเร็จ'
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      // Best-effort: JWT is stateless, so logout is really a client-side
      // token clear. The API call lets the backend log/audit it, but we
      // don't want a network failure to block the user from logging out.
      await authApi.logout()
    } catch {
      // ignore — clearing local auth still proceeds below
    } finally {
      clearAuth()
    }
  }

  // Re-hydrates `user` from an existing token (e.g. on app boot / page
  // reload). Clears auth if the token is invalid or expired.
  async function fetchMe() {
    if (!token.value) return false
    loading.value = true
    try {
      const res = await authApi.getMe()
      if (res.data.success && res.data.data) {
        user.value = res.data.data
        return true
      }
      clearAuth()
      return false
    } catch {
      clearAuth()
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    setAuth,
    clearAuth,
    login,
    register,
    logout,
    fetchMe
  }
})
