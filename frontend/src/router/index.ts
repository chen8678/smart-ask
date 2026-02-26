import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/AppSimple.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue')
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: () => import('@/views/KnowledgeBase.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/simple-query',
      name: 'simple-query',
      component: () => import('@/views/SimpleQuery.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/voice-qa',
      name: 'voice-qa',
      component: () => import('@/views/VoiceQA.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/simple-kb',
      name: 'simple-kb',
      component: () => import('@/views/SimpleKB.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/bim-qa',
      name: 'bim-qa',
      component: () => import('@/views/BIMKnowledgeQA.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/financial',
      name: 'financial',
      component: () => import('@/views/FinancialCompliance.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/medical',
      name: 'medical',
      component: () => import('@/views/MedicalAssistant.vue'),
      meta: { requiresAuth: true }
    },
    // 教育助手模块（替换原学习分析）
    {
      path: '/learning-analytics',
      name: 'learning-analytics',
      component: () => import('@/views/EducationAssistant.vue'),
      meta: { requiresAuth: true }
    },
    // 课程管理模块（保留用于管理员）
    {
      path: '/courses',
      name: 'courses',
      component: () => import('@/views/Courses.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/courses/:id',
      name: 'course-detail',
      component: () => import('@/views/CourseDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/ai-models',
      name: 'ai-models',
      component: () => import('@/views/AIModelConfig.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/Admin.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
  ]
})

// 路由守卫：未登录访问需认证页面时跳转登录
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.loadUser()
  if (to.meta.requiresAuth === false) {
    next()
    return
  }
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  if (to.meta.requiresAdmin && (!authStore.isAuthenticated || !authStore.user?.is_staff)) {
    next('/')
    return
  }
  next()
})

export default router
