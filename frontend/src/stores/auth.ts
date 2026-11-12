import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiRequest } from '../api/client'

export interface User {
  id: number
  email: string
  full_name: string
  role: 'STUDENT' | 'STAFF' | 'ADMIN'
  student_index?: string
  faculty?: string
  department_id?: number
  is_active: boolean
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<User | null>(null)
  const isAuthenticated = computed(() => currentUser.value !== null)
  const isStudent = computed(() => currentUser.value?.role === 'STUDENT')
  const isStaff = computed(() => currentUser.value?.role === 'STAFF' || currentUser.value?.role === 'ADMIN')
  const isAdmin = computed(() => currentUser.value?.role === 'ADMIN')
  const isLoading = ref<boolean>(false)

  async function checkAuth(): Promise<boolean> {
    try {
      isLoading.value = true
      const user = await apiRequest<User>('/api/auth/me')
      currentUser.value = user
      return true
    } catch {
      currentUser.value = null
      localStorage.removeItem('apex_token')
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function login(email: string, password: string): Promise<User> {
    isLoading.value = true
    try {
      const res = await apiRequest<{ access_token: string; user: User }>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      currentUser.value = res.user
      localStorage.setItem('apex_token', res.access_token)
      return res.user
    } finally {
      isLoading.value = false
    }
  }

  async function register(data: {
    email: string
    password: string
    full_name: string
    student_index?: string
    faculty?: string
  }): Promise<User> {
    isLoading.value = true
    try {
      await apiRequest<User>('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      // Auto login after registration
      return await login(data.email, data.password)
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await apiRequest('/api/auth/logout', { method: 'POST' })
    } catch {
      // Ignore network failures on logout
    } finally {
      currentUser.value = null
      localStorage.removeItem('apex_token')
    }
  }

  async function quickSwitchDemo(role: 'student' | 'student2' | 'staff' | 'admin'): Promise<void> {
    const creds = {
      student: { email: 'student@apex.edu.lk', password: 'student123' },
      student2: { email: 'sanduni@apex.edu.lk', password: 'student123' },
      staff: { email: 'staff@apex.edu.lk', password: 'staff123' },
      admin: { email: 'admin@apex.edu.lk', password: 'admin123' },
    }
    const target = creds[role]
    if (target) {
      await login(target.email, target.password)
    }
  }

  return {
    currentUser,
    isAuthenticated,
    isStudent,
    isStaff,
    isAdmin,
    isLoading,
    checkAuth,
    login,
    register,
    logout,
    quickSwitchDemo,
  }
})
