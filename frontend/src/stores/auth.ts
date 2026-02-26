import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export interface User {
  id: string
  username: string
  email: string
  role: string
  is_staff: boolean
  is_superuser: boolean
  profile: Record<string, any>
  preferences: Record<string, any>
  created_at: string
  last_login_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  
  const isAuthenticated = computed(() => !!user.value && !!token.value)

  const login = async (credentials: { username: string; password: string }) => {
    try {
      const response = await api.post('/auth/login/', credentials)
      const { access, user: userData } = response.data
      
      token.value = access
      user.value = userData
      
      localStorage.setItem('token', access)
      localStorage.setItem('user', JSON.stringify(userData))
      
      ElMessage.success('登录成功')
      return response.data
    } catch (error: any) {
      const data = error.response?.data
      const msg = data?.detail || data?.error || (typeof data?.username === 'string' ? data.username : Array.isArray(data?.non_field_errors) ? data.non_field_errors[0] : null) || '登录失败'
      ElMessage.error(msg)
      throw error
    }
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    password_confirm: string
    role?: string
  }) => {
    try {
      const response = await api.post('/auth/register/', userData)
      const { access, user: newUser } = response.data
      
      token.value = access
      user.value = newUser
      
      localStorage.setItem('token', access)
      localStorage.setItem('user', JSON.stringify(newUser))
      
      ElMessage.success('注册成功')
      return response.data
    } catch (error: any) {
      ElMessage.error(error.response?.data?.error || '注册失败')
      throw error
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
  }

  const loadUser = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      user.value = JSON.parse(storedUser)
    }
  }

  return {
    user: readonly(user),
    token: readonly(token),
    isAuthenticated,
    login,
    register,
    logout,
    loadUser
  }
})
