<template>
  <div class="education-shell">
    <section class="education-hero">
      <video class="hero-video" autoplay muted loop playsinline>
        <source :src="educationVideoSrc" type="video/mp4" />
      </video>
      <div class="hero-overlay"></div>
      <div class="hero-header">
        <div>
          <p class="eyebrow">教育 · 智能助手</p>
          <h1>学习路径规划与教学资源库</h1>
          <p class="subtitle">
            输入学习问题或目标，AI 生成个性化学习路径；浏览教学资源库，获取课程与知识点。
          </p>
        </div>
        <el-button text class="text-link" @click="goHome">
          <AppleIcon name="arrow-left" :size="16" />
          返回首页
        </el-button>
      </div>
    </section>

    <div class="content-grid">
      <section class="column-card column-card--assistant">
        <div class="column-header">
          <div>
            <p class="eyebrow">学习助手</p>
            <h3>智能学习路径规划</h3>
          </div>
          <el-tag type="success" size="small">Beta</el-tag>
        </div>

        <el-form :model="learningForm" label-position="top" class="learning-form">
          <el-form-item label="学习目标或问题">
            <el-input
              v-model="learningForm.query"
              type="textarea"
              :rows="4"
              placeholder="例如：我想学习 Python 编程基础，或者：如何理解微积分中的导数概念？"
            />
          </el-form-item>

          <el-form-item label="学习类型（可选）">
            <el-select v-model="learningForm.category" placeholder="请选择学习类型" size="small">
              <el-option label="编程开发" value="programming" />
              <el-option label="数学基础" value="mathematics" />
              <el-option label="语言学习" value="language" />
              <el-option label="科学知识" value="science" />
              <el-option label="职业技能" value="professional" />
            </el-select>
          </el-form-item>

          <div class="pill-row">
            <span
              class="pill"
              :class="{ active: learningForm.query.includes(topic) }"
              v-for="topic in quickTopics"
              :key="topic"
              @click="setQuickTopic(topic)"
            >
              {{ topic }}
            </span>
          </div>

          <div class="form-actions">
            <el-button text @click="resetForm">清空</el-button>
            <el-button type="primary" :loading="generating" @click="generateLearningPath">
              生成学习路径
            </el-button>
          </div>
        </el-form>

        <div class="learning-result" v-if="learningResult">
          <div class="result-header">
            <div>
              <p class="eyebrow">推荐学习路径</p>
              <h3>{{ learningResult.title || '个性化学习计划' }}</h3>
            </div>
            <el-tag type="info">{{ learningResult.steps?.length || 0 }} 个步骤</el-tag>
          </div>
          
          <div class="path-steps" v-if="learningResult.steps">
            <div
              v-for="(step, index) in learningResult.steps"
              :key="index"
              class="step-item"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <h4>{{ step.title }}</h4>
                <p>{{ step.description }}</p>
                <div class="step-tags" v-if="step.resources">
                  <el-tag
                    v-for="resource in step.resources"
                    :key="resource"
                    size="small"
                    type="info"
                    style="margin-right: 6px;"
                  >
                    {{ resource }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
          
          <p class="result-text" v-if="learningResult.explanation">
            {{ learningResult.explanation }}
          </p>
        </div>
        <div v-else class="result-placeholder">
          请输入学习目标或问题，AI 将为您生成个性化的学习路径。
        </div>
      </section>

      <section class="column-card column-card--resources">
        <div class="column-header">
          <div>
            <p class="eyebrow">资源库</p>
            <h3>教学资源与课程</h3>
          </div>
          <el-tag type="info" size="small">{{ visibleResources.length }} 项</el-tag>
        </div>

        <div class="filter-bar">
          <el-select v-model="categoryFilter" placeholder="全部分类" size="small" class="filter-item">
            <el-option label="全部分类" value="all" />
            <el-option
              v-for="category in categoryOptions"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
          <el-select v-model="difficultyFilter" placeholder="全部难度" size="small" class="filter-item">
            <el-option label="全部难度" value="all" />
            <el-option label="入门" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </div>

        <el-skeleton v-if="loadingResources" :rows="4" animated />
        <div v-else class="resource-list">
          <el-empty v-if="!visibleResources.length" description="暂无教学资源" />
          <div v-else>
            <div v-for="resource in visibleResources" :key="resource.id" class="resource-row">
              <div class="resource-badge">
                <el-tag size="small" type="info">{{ resource.category || '通用' }}</el-tag>
                <el-tag
                  size="small"
                  :type="difficultyMap[resource.difficulty]?.tag || 'info'"
                >
                  {{ difficultyMap[resource.difficulty]?.label || '入门' }}
                </el-tag>
              </div>
              <h4>{{ resource.title }}</h4>
              <p>{{ resource.description || '暂无描述' }}</p>
              <div class="resource-meta">
                <span class="meta-item">
                  <AppleIcon name="clock" :size="14" />
                  {{ resource.duration || '未知' }}
                </span>
                <span class="meta-item" v-if="resource.progress !== undefined">
                  <AppleIcon name="trend" :size="14" />
                  进度: {{ resource.progress }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import api from '@/utils/api'
import educationVideo from '@/video/教育.mp4?url'

const router = useRouter()

// 视频资源
const educationVideoSrc = educationVideo

// 学习表单
const learningForm = reactive({
  query: '',
  category: ''
})

const generating = ref(false)
const learningResult = ref<any>(null)

// 快速主题标签
const quickTopics = [
  'Python 基础',
  '微积分入门',
  '英语语法',
  '数据结构',
  '机器学习',
  'Web 开发'
]

// 资源数据
const resources = ref<any[]>([])
const loadingResources = ref(false)
const categoryFilter = ref('all')
const difficultyFilter = ref('all')

const categoryOptions = ['编程开发', '数学基础', '语言学习', '科学知识', '职业技能']

const difficultyMap: Record<string, { label: string; tag: string }> = {
  beginner: { label: '入门', tag: 'success' },
  intermediate: { label: '中级', tag: 'warning' },
  advanced: { label: '高级', tag: 'danger' }
}

const visibleResources = computed(() => {
  let filtered = resources.value

  if (categoryFilter.value !== 'all') {
    filtered = filtered.filter(r => r.category === categoryFilter.value)
  }

  if (difficultyFilter.value !== 'all') {
    filtered = filtered.filter(r => r.difficulty === difficultyFilter.value)
  }

  return filtered
})

const setQuickTopic = (topic: string) => {
  learningForm.query = topic
}

const generateLearningPath = async () => {
  if (!learningForm.query.trim()) {
    ElMessage.warning('请先输入学习目标或问题')
    return
  }

  generating.value = true
  try {
    const response = await api.post('/learning/generate-path/', {
      query: learningForm.query,
      category: learningForm.category
    })
    learningResult.value = response.data
    ElMessage.success('学习路径生成完成')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '生成失败，请稍后再试')
  } finally {
    generating.value = false
  }
}

const resetForm = () => {
  learningForm.query = ''
  learningForm.category = ''
  learningResult.value = null
}

const fetchResources = async () => {
  loadingResources.value = true
  try {
    const response = await api.get('/learning/resources/')
    resources.value = response.data.results || response.data || []
  } catch (error) {
    // 如果 API 不存在，使用模拟数据
    resources.value = [
      {
        id: 1,
        title: 'Python 编程基础',
        description: '从零开始学习 Python 编程语言，掌握基本语法和常用库',
        category: '编程开发',
        difficulty: 'beginner',
        duration: '20 小时',
        progress: 0
      },
      {
        id: 2,
        title: '微积分入门',
        description: '理解导数和积分的基本概念，掌握计算方法',
        category: '数学基础',
        difficulty: 'beginner',
        duration: '15 小时',
        progress: 0
      },
      {
        id: 3,
        title: '数据结构与算法',
        description: '学习常见数据结构和算法，提升编程能力',
        category: '编程开发',
        difficulty: 'intermediate',
        duration: '30 小时',
        progress: 0
      },
      {
        id: 4,
        title: '机器学习基础',
        description: '了解机器学习的基本原理和常用算法',
        category: '科学知识',
        difficulty: 'advanced',
        duration: '40 小时',
        progress: 0
      }
    ]
  } finally {
    loadingResources.value = false
  }
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchResources()
})
</script>

<style scoped>
.education-shell {
  padding: 32px 48px;
  background: var(--apple-body-bg);
  min-height: 100vh;
}

.education-hero {
  position: relative;
  overflow: hidden;
  border-radius: 32px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 90px 60px 70px;
  margin-bottom: 32px;
  min-height: 320px;
  isolation: isolate;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8), 0 40px 90px rgba(10, 10, 15, 0.18);
}

.hero-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.4) 0%,
    rgba(0, 0, 0, 0.2) 50%,
    rgba(0, 0, 0, 0.4) 100%
  );
  z-index: 1;
  backdrop-filter: blur(1px);
}

.hero-header {
  position: relative;
  z-index: 2;
  color: #ffffff;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  padding: 0 12px;
}

.hero-header h1 {
  font-size: 36px;
  font-weight: 700;
  margin: 6px 0 8px;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.hero-header .subtitle {
  margin-bottom: 0;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.hero-header .eyebrow {
  color: rgba(255, 255, 255, 0.85);
}

.intro-card,
.column-card {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-card-radius);
  padding: 28px 32px;
  margin-bottom: 24px;
}

.eyebrow {
  font-size: 13px;
  font-weight: 600;
  color: var(--apple-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.intro-card h2 {
  font-size: 32px;
  font-weight: 700;
  color: var(--apple-text-primary);
  margin: 8px 0 12px;
}

.subtitle {
  font-size: 16px;
  color: var(--apple-text-secondary);
  line-height: 1.5;
}

.text-link {
  color: var(--apple-brand-blue);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.column-card {
  min-height: 520px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.column-card--assistant::before,
.column-card--resources::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 24px 24px 0 0;
}

.column-card--assistant::before {
  background: linear-gradient(90deg, #0a84ff, #5ac8fa);
}

.column-card--resources::before {
  background: linear-gradient(90deg, #30d158, #7ed321);
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.column-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 4px 0 0;
}

.learning-form {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 16px;
  background: rgba(31, 31, 35, 0.04);
}

.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.pill {
  padding: 6px 12px;
  border-radius: var(--apple-pill-radius);
  border: 1px solid var(--apple-border);
  background: var(--apple-surface);
  color: var(--apple-text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.pill:hover {
  background: var(--apple-elevated);
  border-color: var(--apple-brand-blue);
}

.pill.active {
  background: var(--apple-brand-blue);
  color: white;
  border-color: var(--apple-brand-blue);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.learning-result {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
  position: relative;
  background: var(--apple-surface);
}

.learning-result::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(10, 132, 255, 0.15);
  pointer-events: none;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 4px 0 0;
}

.path-steps {
  margin: 16px 0;
}

.step-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(10, 132, 255, 0.05);
  border: 1px solid rgba(10, 132, 255, 0.1);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--apple-brand-blue);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 0 0 6px;
}

.step-content p {
  font-size: 14px;
  color: var(--apple-text-secondary);
  margin: 0 0 8px;
  line-height: 1.5;
}

.step-tags {
  margin-top: 8px;
}

.result-text {
  font-size: 14px;
  color: var(--apple-text-secondary);
  line-height: 1.6;
  margin-top: 12px;
}

.result-placeholder {
  border: 1px dashed var(--apple-border);
  border-radius: 20px;
  padding: 24px;
  color: var(--apple-text-secondary);
  text-align: center;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.filter-item {
  min-width: 160px;
}

.filter-bar :deep(.el-input__wrapper) {
  border: 1px solid var(--apple-border);
  box-shadow: none !important;
  border-radius: var(--apple-control-radius);
}

.resource-list {
  flex: 1;
  overflow: auto;
  padding-right: 8px;
}

.resource-row {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.resource-row:hover {
  border-color: var(--apple-brand-blue);
  box-shadow: 0 2px 8px rgba(10, 132, 255, 0.1);
}

.resource-row h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 8px 0;
}

.resource-row p {
  font-size: 14px;
  color: var(--apple-text-secondary);
  margin-bottom: 8px;
  line-height: 1.5;
}

.resource-badge {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.resource-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--apple-text-tertiary);
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 768px) {
  .education-shell {
    padding: 24px;
  }

  .education-hero {
    padding: 60px 20px 40px;
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-item,
  .learning-form {
    width: 100%;
  }

  .hero-header {
    flex-direction: column;
  }
}
</style>

