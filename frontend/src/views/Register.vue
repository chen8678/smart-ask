<template>
  <div class="register-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
      <div class="floating-shape shape-4"></div>
      <div class="floating-shape shape-5"></div>
    </div>
    
    <!-- 主要内容 -->
    <div class="register-content">
      <!-- 统一的注册模块 -->
      <div class="unified-register-module">
        <!-- 品牌信息 -->
        <div class="brand-section">
          <div class="brand-logo">
            <div class="logo-icon">
              <BrandMark :size="92" />
            </div>
            <h1 class="brand-title">智能知识问答平台</h1>
            <p class="brand-subtitle">大模型驱动的专业领域私有知识库</p>
          </div>
          <div class="brand-features">
            <div class="feature-item">
              <AppleIcon name="bubble.left.and.bubble.right" :size="22" />
              <span>智能问答</span>
            </div>
            <div class="feature-item">
              <AppleIcon name="doc.text" :size="22" />
              <span>私有知识库</span>
            </div>
            <div class="feature-item">
              <AppleIcon name="star" :size="22" />
              <span>大模型驱动</span>
            </div>
          </div>
        </div>
        
        <!-- 注册表单 -->
        <div class="form-section">
          <el-card class="register-card">
            <div class="card-header">
              <h2>创建账号</h2>
              <p>加入AI智能问答系统</p>
            </div>
            
            <el-form
              ref="registerFormRef"
              :model="registerForm"
              :rules="rules"
              label-width="0"
              size="large"
              class="register-form"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  class="form-input"
                >
                  <template #prefix>
                    <AppleIcon name="person" :size="16" />
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱"
                  class="form-input"
                >
                  <template #prefix>
                    <AppleIcon name="envelope" :size="16" />
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
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
              
              <el-form-item prop="password_confirm">
                <el-input
                  v-model="registerForm.password_confirm"
                  type="password"
                  placeholder="请确认密码"
                  class="form-input"
                  show-password
                >
                  <template #prefix>
                    <AppleIcon name="lock.fill" :size="16" />
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item class="form-actions">
                <el-button
                  type="primary"
                  @click="handleRegister"
                  :loading="loading"
                  class="register-button"
                  size="large"
                >
                  <AppleIcon name="person.badge.plus" :size="18" />
                  注册
                </el-button>
              </el-form-item>
              
              <div class="form-footer">
                <span class="login-text">已有账号？</span>
                <el-button
                  @click="handleLogin"
                  type="text"
                  class="login-button"
                >
                  立即登录
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
import { useAuthStore } from '@/stores/auth'
import BrandMark from '@/components/BrandMark.vue'
import AppleIcon from '@/components/AppleIcon.vue'

const router = useRouter()
const authStore = useAuthStore()

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const loading = ref(false)
const registerFormRef = ref()

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        const payload = {
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          password_confirm: registerForm.password_confirm
        }
        await authStore.register(payload)
        router.push('/')
      } catch (error) {
        // 错误已在store中处理
      } finally {
        loading.value = false
      }
    }
  })
}

const handleLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
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

.register-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  z-index: 1;
  padding: 24px;
}

.unified-register-module {
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

.register-card {
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

.register-button {
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

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 30px 50px rgba(10, 132, 255, 0.4);
}

.form-footer {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  text-align: center;
}

.login-text {
  color: var(--apple-text-secondary);
  margin-right: 6px;
}

.login-button {
  color: var(--apple-brand-blue);
  font-weight: 600;
  border-radius: 999px;
  padding: 6px 18px;
}

.login-button:hover {
  background: rgba(10, 132, 255, 0.12);
}

@media (max-width: 900px) {
  .unified-register-module {
    flex-direction: column;
    max-width: 100%;
  }

  .brand-section,
  .form-section {
    padding: 40px 28px;
  }

  .register-content {
    padding: 16px;
  }
}
</style>
