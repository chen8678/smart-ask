<template>
  <div class="home-page">
    <header class="top-nav">
      <div class="brand">
        <BrandMark class="brand-logo" :size="48" circular />
        <span class="brand-title">智库通</span>
        <span class="brand-subtitle">Private Knowledge Intelligence</span>
        </div>
      <div class="nav-actions">
        <template v-if="authStore.isAuthenticated">
          <el-button text class="text-link" @click="goToKnowledge">控制台</el-button>
            <el-dropdown @command="handleCommand">
            <el-button text class="user-pill">
              <AppleIcon name="user" :size="18" />
                {{ authStore.user?.username }}
              <AppleIcon name="chevron-down" :size="14" />
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item v-if="authStore.user?.is_staff || authStore.user?.is_superuser" command="admin">系统管理</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
        </template>
        <template v-else>
          <el-button text class="text-link" @click="goToLogin">登录</el-button>
          <el-button text class="text-link" @click="goToRegister">注册</el-button>
        </template>
          </div>
    </header>

    <main class="page-main">
      <section class="hero-card">
        <div class="hero-left">
          <p class="eyebrow">智库通 · 通用知识工作台</p>
          <h1>知识库与智能问答，一站式交付</h1>
          <p class="hero-subtitle">
            统一底座负责知识汇聚、治理与安全；
            问答引擎直接消费这些知识，企业无需二次集成。
          </p>
          <div class="hero-feature-list">
            <div class="hero-feature-card">
              <div class="feature-head">
                <AppleIcon name="document" :size="20" />
                <div>
                  <h3>知识库</h3>
                  <p>多格式文档统一治理、标签与版本可追溯</p>
          </div>
        </div>
              <el-button type="primary" size="large" class="wide-button" @click="goToKnowledge">
                进入知识库
            </el-button>
          </div>
            <div class="hero-feature-card">
              <div class="feature-head">
                <AppleIcon name="chat" :size="20" />
                <div>
                  <h3>智能问答</h3>
                  <p>多模型协同输出，引用可追溯、可审批</p>
        </div>
      </div>
              <el-button size="large" class="outline-button wide-button" @click="goToChat">
                体验问答
              </el-button>
              </div>
            </div>
              </div>
        <div class="hero-right">
          <BrandMark class="hero-watermark" :size="120" />
          <div class="hero-graphic">
            <span class="graphic-glow graphic-glow--primary"></span>
            <span class="graphic-glow graphic-glow--secondary"></span>
            <svg class="hero-svg" viewBox="0 0 240 160" role="presentation" aria-hidden="true">
              <defs>
                <linearGradient id="heroGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#0a84ff" />
                  <stop offset="50%" stop-color="#5ac8fa" />
                  <stop offset="100%" stop-color="#a5b4fc" />
                </linearGradient>
                <filter id="heroShadow" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="rgba(10,132,255,0.25)" />
                </filter>
              </defs>
              <path
                class="hero-arc"
                d="M10 120 C40 20, 200 20, 230 120"
                stroke="url(#heroGradient)"
                fill="none"
                stroke-width="8"
                stroke-linecap="round"
                filter="url(#heroShadow)"
              />
              <circle class="hero-node hero-node--one" cx="50" cy="60" r="6" />
              <circle class="hero-node hero-node--two" cx="190" cy="70" r="6" />
              <circle class="hero-node hero-node--three" cx="120" cy="110" r="5" />
            </svg>
            <div class="graphic-card graphic-card--primary">
              <p>实时问答</p>
              <span>结合专属知识，生成可信答案</span>
            </div>
            <div class="graphic-card graphic-card--secondary">
              <p>行业助手</p>
              <span>金融 / 医疗场景即开即用</span>
            </div>
          </div>
              </div>
      </section>

      <section v-if="authStore.isAuthenticated" class="industry-panel">
        <div class="panel-header">
            <div>
            <p class="eyebrow">行业扩展包</p>
            <h2>基于通用底座的可插拔行业能力</h2>
            <p class="panel-subtitle">行业模块只是扩展包，沿用同一个知识库与问答引擎，仅叠加金融 / 医疗 / 教育的规则与风控。</p>
              </div>
            </div>
          <div class="industry-grid">
          <div class="industry-card" @click="goToFinancial">
            <div>
              <p class="industry-tag">金融 · 合规</p>
              <h3>政策时间轴 + 风险检查</h3>
              <p>集中管理监管通知、版本变更与业务风险输出。</p>
              </div>
            <div class="industry-stats">
              <div class="stat-chip">
                <strong>3</strong>
                <span>核心流程</span>
            </div>
              <div class="stat-chip">
                <strong>7</strong>
                <span>策略规则</span>
          </div>
        </div>
      </div>
          <div class="industry-card" @click="goToMedical">
            <div>
              <p class="industry-tag">医疗 · 智能诊疗</p>
              <h3>症状匹配 + 药品知识</h3>
              <p>支持多症状输入、药品交互与风险提醒。</p>
            </div>
            <div class="industry-stats">
              <div class="stat-chip">
                <strong>50+</strong>
                <span>症状词条</span>
          </div>
              <div class="stat-chip">
                <strong>10+</strong>
                <span>药品条目</span>
              </div>
                </div>
              </div>
          <div class="industry-card" @click="goToLearningAnalytics">
            <div>
              <p class="industry-tag">教育 · 智能助手</p>
              <h3>学习路径规划 + 教学资源库</h3>
              <p>基于通用知识库生成个性化学习路径与资源推荐。</p>
              </div>
            <div class="industry-stats">
              <div class="stat-chip">
                <strong>多场景</strong>
                <span>学习类型</span>
                </div>
              <div class="stat-chip">
                <strong>个性化</strong>
                <span>路径生成</span>
              </div>
          </div>
        </div>
      </div>
      </section>

      <section v-if="authStore.isAuthenticated" class="stats-panel">
        <div class="stats-head">
          <div>
            <p class="eyebrow">我的数据</p>
            <h2>知识与问答脉搏</h2>
            <p class="panel-subtitle">这些指标仅自己可见，用于掌握知识库与问答的日常健康度。</p>
          </div>
          <el-button class="ghost-button" :loading="loading" @click="loadStats">
            <AppleIcon name="refresh" :size="16" />
            刷新
            </el-button>
          </div>
        <div v-if="stats" class="stats-card-grid">
          <div v-for="card in statCards" :key="card.key" class="stats-card">
            <div class="stats-card-top">
              <span class="stat-icon-pill" :class="`tone-${card.tone}`">
                <AppleIcon :name="card.icon" :size="16" />
              </span>
              <span class="stat-label">{{ card.label }}</span>
              </div>
            <strong>{{ card.value }}</strong>
            <p>{{ card.description }}</p>
              </div>
            </div>
        <div v-else class="stats-empty">
          <AppleIcon class="is-loading" name="loading" :size="18" :spin="true" />
          <span>正在加载最新数据...</span>
              </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import BrandMark from '@/components/BrandMark.vue'
import api from '@/utils/api'
import type { AppleIconName } from '@/icons/apple'

const router = useRouter()
const authStore = useAuthStore()

type DashboardStats = {
  total_documents: number
  total_questions: number
  knowledge_bases: number
  content_generated: number
}

const loading = ref(false)
const stats = ref<DashboardStats | null>(null)
type StatCard = {
  key: string
  label: string
  description: string
  icon: AppleIconName
  tone: 'blue' | 'green' | 'orange' | 'purple'
  value: number
}

// 导航方法
const statCards = computed<StatCard[]>(() => {
  if (!stats.value) {
    return []
  }
  return [
    {
      key: 'documents',
      label: '文档总数',
      description: '已经汇入的知识片段',
      icon: 'document',
      tone: 'blue',
      value: stats.value.total_documents ?? 0
    },
    {
      key: 'questions',
      label: '问答次数',
      description: '近期开启的问答交互',
      icon: 'chat',
      tone: 'green',
      value: stats.value.total_questions ?? 0
    },
    {
      key: 'knowledge',
      label: '知识库数量',
      description: '当前维护的知识库集合',
      icon: 'folder',
      tone: 'orange',
      value: stats.value.knowledge_bases ?? 0
    },
    {
      key: 'content',
      label: '生成内容次数',
      description: '触发创作或总结的次数',
      icon: 'bolt',
      tone: 'purple',
      value: stats.value.content_generated ?? 0
    }
  ]
})

const goToKnowledge = () => {
  router.push('/knowledge')
}

const goToChat = () => {
  router.push('/chat')
}

const goToLearningAnalytics = () => {
  router.push('/learning-analytics')
}

const goToFinancial = () => {
  router.push('/financial')
}

const goToMedical = () => {
  router.push('/medical')
}

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

// 用户操作
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
    case 'admin':
      router.push('/admin')
      break
    case 'logout':
      authStore.logout()
      router.push('/login')
      break
  }
}

// 加载统计数据
const loadStats = async () => {
  loading.value = true
  try {
    // 调用用户专用的统计API，而不是系统级统计
    const response = await api.get('/chat/dashboard-stats/')
    stats.value = {
      total_documents: response.data.documents || 0,
      total_questions: response.data.questions || 0,
      knowledge_bases: response.data.knowledgeBases || 0,
      content_generated: response.data.content_generated || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 只有在用户已登录时才加载统计数据
  if (authStore.isAuthenticated) {
    loadStats()
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f5f7;
  padding: 32px 48px 80px;
  color: #1f1f1f;
  --space-lg: 32px;
  --space-md: 16px;
  --card-radius: 24px;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.brand {
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: relative;
  padding-left: 64px;
}

.brand-logo {
  position: absolute;
  left: 0;
  top: -4px;
  transform: rotate(-6deg);
}

.brand-title {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.1em;
}

.brand-subtitle {
  font-size: 12px;
  color: #8e8e93;
}

.nav-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.text-link {
  color: #1f1f1f;
  font-weight: 500;
}

.user-pill {
  border: 1px solid #e5e5ea;
  border-radius: 999px;
  padding: 6px 16px;
}

.page-main {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.hero-card,
.function-panel,
.industry-panel,
.stats-panel {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  border: 1px solid #ededf0;
}

.hero-card {
  padding: 28px 28px 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  align-items: center;
}

.hero-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16px;
}

.hero-left h1 {
  font-size: 42px;
  margin: 12px 0;
  line-height: 1.15;
}

.hero-subtitle {
  font-size: 18px;
  color: #3a3a3c;
  margin: 0;
  line-height: 1.5;
}

.hero-feature-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin: 20px 0 0;
}

.hero-feature-card {
  border: 1px solid rgba(10, 132, 255, 0.12);
  border-radius: 20px;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.92);
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 20px 40px rgba(10, 10, 15, 0.08);
}

.feature-head {
  display: flex;
  gap: 12px;
  align-items: center;
}

.feature-head h3 {
  margin: 0;
  font-size: 16px;
}

.feature-head p {
  margin: 2px 0 0;
  color: #6d6d72;
  font-size: 13px;
}

.eyebrow {
  font-size: 12px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #8e8e93;
}

.description {
  color: #6d6d72;
  line-height: 1.6;
}

.hero-actions {
  margin-top: 24px;
  display: flex;
  gap: 16px;
}

.outline-button {
  border: 1px solid #e0e0e5;
  color: #1f1f1f;
}

.outline-button:hover {
  border-color: #0a84ff;
  color: #0a84ff;
}

.wide-button {
  width: 100%;
}

.stats-panel {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(10, 10, 15, 0.06);
  box-shadow: 0 24px 60px rgba(15, 15, 15, 0.08);
}

.stats-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.stats-card-grid {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.stats-card {
  border: 1px solid rgba(10, 10, 15, 0.06);
  border-radius: 20px;
  padding: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.85), rgba(245, 245, 247, 0.9));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.stats-card-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.stat-icon-pill {
  width: 32px;
  height: 32px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-pill.tone-blue {
  background: rgba(10, 132, 255, 0.12);
  color: #0a84ff;
}

.stat-icon-pill.tone-green {
  background: rgba(48, 209, 88, 0.12);
  color: #30d158;
}

.stat-icon-pill.tone-orange {
  background: rgba(255, 159, 10, 0.12);
  color: #ff9f0a;
}

.stat-icon-pill.tone-purple {
  background: rgba(191, 90, 242, 0.12);
  color: #bf5af2;
}

.stats-card strong {
  font-size: 26px;
  margin: 0;
  display: block;
}

.stats-card p {
  margin: 4px 0 0;
  color: #6d6d72;
  font-size: 13px;
}

.ghost-button {
  border: 1px solid rgba(10, 10, 15, 0.08);
  color: #1f1f1f;
}

.ghost-button:hover {
  border-color: #0a84ff;
  color: #0a84ff;
}

.hero-right {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.hero-watermark {
  position: absolute;
  top: -18px;
  right: -18px;
  opacity: 0.35;
  transform: rotate(-8deg);
  pointer-events: none;
}

.hero-graphic {
  position: relative;
  width: 100%;
  max-width: 360px;
  border-radius: 28px;
  padding: 32px 28px 36px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 25px 55px rgba(15, 15, 15, 0.12), inset 0 0 0 1px rgba(255, 255, 255, 0.4);
  overflow: hidden;
  backdrop-filter: blur(18px);
  animation: glassPulse 9s ease-in-out infinite;
}

.hero-graphic::after {
  content: '';
  position: absolute;
  inset: 8px;
  border-radius: 24px;
  border: 1px solid rgba(10, 132, 255, 0.08);
  pointer-events: none;
}

.graphic-glow {
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
  animation: glowDrift 16s ease-in-out infinite;
}

.graphic-glow--primary {
  top: -40px;
  right: -60px;
  background: radial-gradient(circle, rgba(10, 132, 255, 0.35), transparent 60%);
}

.graphic-glow--secondary {
  bottom: -80px;
  left: -40px;
  background: radial-gradient(circle, rgba(191, 90, 242, 0.3), transparent 65%);
  animation-delay: -6s;
}

.hero-svg {
  position: relative;
  width: 100%;
  height: 180px;
  margin-bottom: 20px;
  z-index: 1;
}

.hero-arc {
  stroke-dasharray: 520;
  stroke-dashoffset: 520;
  animation: arcDraw 8s ease-in-out infinite;
}

.hero-node {
  stroke: rgba(255, 255, 255, 0.65);
  stroke-width: 2;
  filter: drop-shadow(0 8px 18px rgba(10, 10, 10, 0.18));
}

.hero-node--one {
  fill: #0a84ff;
  animation: nodePulse 6s ease-in-out infinite;
}

.hero-node--two {
  fill: #a5b4fc;
  animation: nodePulse 7s ease-in-out infinite;
}

.hero-node--three {
  fill: #34c759;
  animation: nodePulse 5s ease-in-out infinite;
}

.graphic-card {
  position: relative;
  background: rgba(245, 245, 247, 0.92);
  border-radius: 18px;
  padding: 18px 20px;
  margin-bottom: 14px;
  box-shadow: 0 10px 24px rgba(15, 15, 15, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
  animation: floatCard 7s ease-in-out infinite;
}

.graphic-card--secondary {
  animation-delay: -3s;
}

.graphic-card p {
  font-weight: 600;
  margin-bottom: 4px;
  color: #1f1f1f;
}

.graphic-card span {
  color: #6d6d72;
  font-size: 14px;
}

@keyframes arcDraw {
  0% {
    stroke-dashoffset: 520;
  }
  35% {
    stroke-dashoffset: 0;
  }
  65% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -520;
  }
}

@keyframes nodePulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.25);
    opacity: 0.75;
  }
}

@keyframes floatCard {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes glowDrift {
  0% {
    transform: translate(-10px, -10px) scale(0.95);
  }
  50% {
    transform: translate(20px, 10px) scale(1.1);
  }
  100% {
    transform: translate(-10px, -5px) scale(0.95);
  }
}

@keyframes glassPulse {
  0%,
  100% {
    box-shadow: 0 25px 55px rgba(15, 15, 15, 0.12), inset 0 0 0 1px rgba(255, 255, 255, 0.4);
  }
  50% {
    box-shadow: 0 30px 60px rgba(15, 15, 15, 0.16), inset 0 0 0 1px rgba(10, 132, 255, 0.2);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.panel-subtitle {
  margin-top: 8px;
  color: #6d6d72;
  font-size: 15px;
  max-width: 620px;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.function-card {
  border: 1px solid #ededf0;
  border-radius: 20px;
  padding: 24px;
  background: #fafafa;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.function-card:hover {
  transform: translateY(-6px);
  border-color: #0a84ff;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(10, 132, 255, 0.08);
  display: inline-flex;
    align-items: center;
  justify-content: center;
}

.function-card h3 {
  margin: 0;
  font-size: 18px;
}

.function-card p {
  margin: 0;
  color: #6d6d72;
  line-height: 1.5;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
}

.card-tags span {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(10, 132, 255, 0.08);
  color: #0a84ff;
}

.function-card--primary {
  background: #f7fbff;
  border-color: rgba(10, 132, 255, 0.2);
  cursor: pointer;
}

.function-panel--extensions {
  background: #fafafa;
}

.extension-grid .function-card {
  background: #fff;
  border-color: #ededf0;
}

.card-icon--ghost {
  background: rgba(10, 132, 255, 0.05);
}

.card-tag {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(10, 132, 255, 0.08);
  color: #0a84ff;
  font-size: 12px;
  margin: 4px 0 8px;
}

.function-grid .function-card {
  cursor: pointer;
}

.industry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.industry-card {
  border: 1px solid #ededf0;
  border-radius: 20px;
  padding: 24px;
  display: flex;
    flex-direction: column;
  gap: 16px;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.industry-card:hover {
  border-color: #0071e3;
}

.industry-tag {
  font-size: 12px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #8e8e93;
  margin-bottom: 8px;
}

.industry-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat-chip {
  border: 1px solid #e5e5ea;
  border-radius: 16px;
  padding: 10px 14px;
  display: flex;
  align-items: baseline;
  gap: 6px;
  font-size: 13px;
  color: #6d6d72;
}

.stat-chip strong {
  font-size: 18px;
  color: #1f1f1f;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f2f2f7;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row strong {
  font-size: 20px;
}

.stats-empty {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8e8e93;
}

@media (max-width: 768px) {
  .home-page {
    padding: 24px 20px 60px;
  }

  .top-nav {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .hero-actions {
    flex-direction: column;
  }

  .stat-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>

