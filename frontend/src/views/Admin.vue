<template>
  <div class="admin-container">
    <!-- 顶部导航 -->
    <el-header class="admin-header">
      <div class="header-content">
        <div class="logo">
          <h1>系统管理</h1>
        </div>
        <div class="header-actions">
          <el-button @click="goBack" type="info" size="large">
            <el-icon><ArrowLeft /></el-icon>
            返回首页
          </el-button>
          <el-dropdown @command="handleCommand">
            <el-button class="user-button">
              <el-icon><User /></el-icon>
              {{ authStore.user?.username }}
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="admin-main">
      <!-- 统计概览 -->
      <div class="stats-section">
        <div class="container">
          <h2 class="section-title">系统概览</h2>
          <div class="stats-grid" v-if="stats">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon size="24"><User /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.total_users || 0 }}</div>
                <div class="stat-label">用户总数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon size="24"><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.total_documents || 0 }}</div>
                <div class="stat-label">文档总数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon size="24"><Reading /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.total_courses || 0 }}</div>
                <div class="stat-label">课程总数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon size="24"><ChatDotRound /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.total_questions || 0 }}</div>
                <div class="stat-label">问答次数</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 管理功能 -->
      <div class="management-section">
        <div class="container">
          <h2 class="section-title">管理功能</h2>
          <div class="management-grid">
            <!-- 用户管理 -->
            <div class="management-card" @click="goToUserManagement">
              <div class="card-icon">
                <el-icon size="32"><User /></el-icon>
              </div>
              <h3>用户管理</h3>
              <p>管理系统用户和权限</p>
            </div>

            <!-- 知识库管理 -->
            <div class="management-card" @click="goToKnowledgeManagement">
              <div class="card-icon">
                <el-icon size="32"><Document /></el-icon>
              </div>
              <h3>知识库管理</h3>
              <p>管理文档和知识库</p>
            </div>

            <!-- 课程管理 -->
            <div class="management-card" @click="goToCourseManagement">
              <div class="card-icon">
                <el-icon size="32"><Reading /></el-icon>
              </div>
              <h3>课程管理</h3>
              <p>管理学习课程</p>
            </div>

            <!-- 系统配置 -->
            <div class="management-card" @click="goToSystemConfig">
              <div class="card-icon">
                <el-icon size="32"><Setting /></el-icon>
              </div>
              <h3>系统配置</h3>
              <p>配置AI模型和设置</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="quick-actions-section">
        <div class="container">
          <div class="quick-actions">
            <el-button type="primary" @click="refreshStats" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
            <el-button type="info" @click="openDjangoAdmin">
              <el-icon><Setting /></el-icon>
              Django后台
            </el-button>
          </div>
        </div>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { 
  User, 
  Document, 
  Reading, 
  ChatDotRound, 
  Setting, 
  ArrowLeft, 
  ArrowDown,
  Refresh
} from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const stats = ref(null)

const goBack = () => {
  router.push('/')
}

const loadStats = async () => {
  loading.value = true
  try {
    const response = await api.get('/system/stats/')
    stats.value = response.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

const refreshStats = () => {
  loadStats()
}

const openDjangoAdmin = () => {
  window.open('http://localhost:8000/admin/', '_blank')
}

const goToUserManagement = () => {
  ElMessage.info('用户管理功能开发中...')
}

const goToKnowledgeManagement = () => {
  router.push('/knowledge')
}

const goToCourseManagement = () => {
  router.push('/courses')
}

const goToSystemConfig = () => {
  ElMessage.info('系统配置功能开发中...')
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中...')
      break
    case 'logout':
      authStore.logout()
      router.push('/login')
      break
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
}

.admin-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(102, 126, 234, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* Header Styles */
.admin-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 2rem;
  height: 70px;
  display: flex;
  align-items: center;
  position: relative;
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-button {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 10px;
  padding: 8px 16px;
  color: #2c3e50;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-button:hover {
  background: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Main Content */
.admin-main {
  padding: 0;
  position: relative;
  z-index: 5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 3rem;
}

/* Stats Section */
.stats-section {
  padding: 4rem 2rem;
  background: white;
  margin: 2rem;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  box-shadow: 
    0 8px 25px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.stat-item:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.stat-icon {
  width: 50px;
  height: 50px;
  background: rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.stat-item:hover .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: scale(1.1);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
}

/* Management Section */
.management-section {
  padding: 4rem 2rem;
  background: white;
  margin: 2rem;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.management-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.management-card {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  transform-style: preserve-3d;
  perspective: 1000px;
}

.management-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.management-card:hover::before {
  transform: scaleX(1);
}

.management-card:hover {
  transform: translateY(-12px) rotateX(5deg) rotateY(5deg) scale(1.02);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(102, 126, 234, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border-color: #667eea;
}

.card-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  color: white;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform-style: preserve-3d;
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.management-card:hover .card-icon {
  transform: translateZ(20px) rotateY(10deg) rotateX(5deg) scale(1.1);
  box-shadow: 
    0 15px 35px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.management-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.management-card p {
  color: #6c757d;
  line-height: 1.6;
  font-size: 1rem;
}

/* Quick Actions Section */
.quick-actions-section {
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 2rem;
  border-radius: 16px;
  color: white;
}

.quick-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive Design */
@media (max-width: 768px) {
  .management-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .section-title {
    font-size: 2rem;
  }
}
</style>