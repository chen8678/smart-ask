import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000, // 增加到120秒，适应大文档AI回答和知识库检索的时间
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 如果是 FormData，让浏览器自动设置 Content-Type（包含 boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      console.log('API 401 error:', {
        url: error.config?.url,
        pathname: window.location.pathname
      })
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 只有在需要认证的页面才重定向到登录页
      // 首页等公开页面不应该被重定向
      if (window.location.pathname !== '/' && window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        console.log('Redirecting to login due to 401')
        window.location.href = '/login'
      } else {
        console.log('Not redirecting due to public page')
      }
    }
    return Promise.reject(error)
  }
)

export default api
