<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
      <div class="floating-shape shape-4"></div>
      <div class="floating-shape shape-5"></div>
    </div>
    
    <!-- 主要内容 -->
    <div class="login-content">
      <!-- 统一的登录模块 -->
      <div class="unified-login-module">
        <!-- 品牌信息 -->
        <div class="brand-section">
          <div class="brand-logo">
            <div class="logo-icon">
              <BrandMark :size="92" />
            </div>
            <h1 class="brand-title">BIM · 智慧工地知识库</h1>
            <p class="brand-subtitle">面向项目的一体化 BIM 数据与智能问答中台</p>
          </div>
          <div class="brand-features">
            <div class="feature-item">
              <AppleIcon name="building.2" :size="22" />
              <span>BIM 模型 / IFC / JSON</span>
            </div>
            <div class="feature-item">
              <AppleIcon name="doc.text" :size="22" />
              <span>案场知识库与规章制度</span>
            </div>
            <div class="feature-item">
              <AppleIcon name="sparkles" :size="22" />
              <span>大模型驱动的现场问答</span>
            </div>
          </div>
        </div>
        
        <!-- 登录表单 -->
        <div class="form-section">
          <el-card class="login-card">
            <div class="card-header">
              <h2>欢迎回来</h2>
              <p>登录您的账户以继续使用</p>
            </div>
            
            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="rules"
              label-width="0"
              size="large"
              class="login-form"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  class="form-input"
                >
                  <template #prefix>
                    <AppleIcon name="person" :size="16" />
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  class="form-input"
                  show-password
                >
                  <template #prefix>
                    <AppleIcon name="lock" :size="16" />
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item class="form-actions">
                <el-button
                  type="primary"
                  @click="handleLogin"
                  :loading="loading"
                  class="login-button"
                  size="large"
                >
                  <AppleIcon name="arrow.right.circle.fill" :size="18" />
                  登录
                </el-button>
              </el-form-item>
              
              <div class="form-footer">
                <span class="register-text">还没有账户？</span>
                <el-button
                  @click="handleRegister"
                  type="text"
                  class="register-button"
                >
                  立即注册
                </el-button>
              </div>
            </el-form>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import BrandMark from '@/components/BrandMark.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const loading = ref(false)
const loginFormRef = ref()

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(loginForm)
        router.push('/')
      } catch (error) {
        // 错误已在store中处理
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9ff 0%, #eef3ff 35%, #ffffff 100%);
  position: relative;
  overflow: hidden;
  color: var(--apple-text-primary);
  font-family: 'SF Pro Display', 'Helvetica Neue', sans-serif;
}

.background-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(10, 132, 255, 0.08);
  animation: float 6s ease-in-out infinite;
  filter: blur(25px);
}

.shape-1 { width: 260px; height: 260px; top: 8%; left: 12%; }
.shape-2 { width: 200px; height: 200px; top: 60%; right: 15%; animation-delay: 1s; background: rgba(191, 90, 242, 0.12); }
.shape-3 { width: 170px; height: 170px; bottom: 18%; left: 22%; animation-delay: 2s; background: rgba(255, 149, 0, 0.1); }
.shape-4 { width: 190px; height: 190px; top: 18%; right: 22%; animation-delay: .5s; }
.shape-5 { width: 130px; height: 130px; bottom: 30%; right: 8%; animation-delay: 1.5s; background: rgba(48, 209, 88, 0.1); }

@keyframes float {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
  50% { transform: translate3d(0, -30px, 0) scale(1.08); }
}

.login-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  z-index: 1;
  padding: 24px;
}

.unified-login-module {
  width: 100%;
  max-width: 1080px;
  min-height: 600px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 32px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(25px);
  box-shadow: 0 35px 75px rgba(15, 23, 42, 0.12);
  display: flex;
  overflow: hidden;
}

.brand-section {
  flex: 1;
  padding: 56px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
}

.brand-logo {
  position: relative;
  z-index: 1;
  margin-bottom: 48px;
}

.logo-icon {
  width: 92px;
  height: 92px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.logo-icon :deep(.brand-mark) {
  width: 100%;
  height: 100%;
}

.brand-title {
  font-size: 34px;
  font-weight: 700;
  margin: 0 0 16px;
  letter-spacing: 0.02em;
  color: var(--apple-text-primary);
}

.brand-subtitle {
  margin: 0;
  font-size: 18px;
  color: var(--apple-text-secondary);
  line-height: 1.6;
}

.brand-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 18px;
  width: 100%;
  position: relative;
  z-index: 1;
}

.feature-item {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--apple-text-primary);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.feature-item:hover {
  transform: translateY(-3px);
  border-color: rgba(10, 132, 255, 0.4);
}

.feature-item :deep(svg) {
  color: #0a84ff;
}

.form-section {
  flex: 1;
  padding: 56px 44px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.06);
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 32px;
  border-radius: 28px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #ffffff;
  box-shadow: 0 30px 60px rgba(15, 23, 42, 0.1);
}

.card-header {
  text-align: center;
  margin-bottom: 28px;
}

.card-header h2 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 600;
  color: var(--apple-text-primary);
}

.card-header p {
  margin: 0;
  color: var(--apple-text-secondary);
  font-size: 16px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: rgba(246, 248, 255, 0.8);
  backdrop-filter: blur(6px);
  box-shadow: none;
  color: var(--apple-text-primary);
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(10, 132, 255, 0.6);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(10, 132, 255, 0.9);
  box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.15);
}

.form-input :deep(.el-input__inner) {
  color: var(--apple-text-primary);
}

.login-button {
  width: 100%;
  height: 52px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(120deg, #0a84ff, #5ac8fa);
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 20px 40px rgba(10, 132, 255, 0.35);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 30px 50px rgba(10, 132, 255, 0.4);
}

.form-footer {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  text-align: center;
}

.register-text {
  color: var(--apple-text-secondary);
  margin-right: 6px;
}

.register-button {
  color: var(--apple-brand-blue);
  font-weight: 600;
  border-radius: 999px;
  padding: 6px 18px;
}

.register-button:hover {
  background: rgba(10, 132, 255, 0.12);
}

@media (max-width: 900px) {
  .unified-login-module {
    flex-direction: column;
    max-width: 100%;
  }

  .brand-section,
  .form-section {
    padding: 40px 28px;
  }

  .login-content {
    padding: 16px;
  }
}
</style>
