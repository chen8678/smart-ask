<template>
  <div class="learning-analytics-container">
    <!-- 顶部导航 -->
    <el-header class="analytics-header">
      <div class="header-content">
        <h2>内容分析</h2>
        <div class="header-actions">
          <el-button type="primary" @click="refreshData">
            <AppleIcon name="refresh" :size="16" />
            刷新数据
          </el-button>
          <el-button @click="exportReport('pdf')">
            <AppleIcon name="document" :size="16" />
            导出PDF
          </el-button>
          <el-button @click="exportReport('excel')">
            <AppleIcon name="document" :size="16" />
            导出Excel
          </el-button>
          <el-button @click="goBack">
            <AppleIcon name="arrow-left" :size="16" />
            返回
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="analytics-main">
      <!-- 内容概览卡片 -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="card-content">
                <div class="card-icon learning-icon">
                  <AppleIcon name="reading" :size="20" />
                </div>
                <div class="card-info">
                  <h3>{{ learningStats.totalCourses || 0 }}</h3>
                  <p>内容课程</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="card-content">
                <div class="card-icon progress-icon">
                  <AppleIcon name="graph" :size="20" />
                </div>
                <div class="card-info">
                  <h3>{{ learningStats.avgProgress || 0 }}%</h3>
                  <p>平均进度</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="card-content">
                <div class="card-icon time-icon">
                  <AppleIcon name="clock" :size="20" />
                </div>
                <div class="card-info">
                  <h3>{{ learningStats.totalHours || 0 }}h</h3>
                  <p>内容时长</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="card-content">
                <div class="card-icon score-icon">
                  <AppleIcon name="star" :size="20" />
                </div>
                <div class="card-info">
                  <h3>{{ learningStats.avgScore || 0 }}</h3>
                  <p>平均得分</p>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 内容进度分析 -->
      <div class="progress-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>内容进度分析</h3>
              <el-button type="text" @click="viewAllProgress">查看全部</el-button>
            </div>
          </template>
          <div class="progress-content">
            <div v-if="learningProgress.length === 0" class="empty-state">
              <el-empty description="暂无内容进度数据">
                <el-button type="primary" @click="startLearning">开始学习</el-button>
              </el-empty>
            </div>
            <div v-else class="progress-list">
              <div 
                v-for="progress in learningProgress" 
                :key="progress.id"
                class="progress-item"
                @click="viewKnowledgeBaseDetail(progress.id)"
              >
                <div class="course-info">
                  <h4>{{ progress.title }}</h4>
                  <p>知识库内容进度</p>
                  <div class="course-meta">
                    <span class="difficulty">知识库</span>
                    <span class="duration">{{ progress.time_spent }}分钟</span>
                    <span class="last-learned">提问: {{ progress.questions_asked }}次</span>
                  </div>
                </div>
                <div class="progress-info">
                  <div class="progress-bar">
                    <el-progress 
                      :percentage="progress.progress" 
                      :stroke-width="8"
                      :show-text="false"
                    />
                    <span class="progress-text">{{ progress.progress }}%</span>
                  </div>
                  <div class="progress-stats">
                    <span>提问 {{ progress.questions_asked }} 次</span>
                    <span>生成内容 {{ progress.content_generated }} 次</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 推荐内容 -->
      <div class="recommendation-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>智能推荐</h3>
              <el-button type="text" @click="refreshRecommendations">刷新推荐</el-button>
            </div>
          </template>
          <div class="recommendation-content">
            <div v-if="recommendations.length === 0" class="empty-state">
              <el-empty description="暂无推荐内容">
                <el-button type="primary" @click="generateRecommendations">生成推荐</el-button>
              </el-empty>
            </div>
            <div v-else class="recommendation-grid">
              <div 
                v-for="item in recommendations" 
                :key="item.id"
                class="recommendation-item"
                @click="viewRecommendation(item)"
              >
                <div class="item-header">
                  <h4>{{ item.title }}</h4>
                  <el-tag :type="getRecommendationType(item.type)">{{ getRecommendationTypeName(item.type) }}</el-tag>
                </div>
                <p class="item-description">{{ item.description }}</p>
                <div class="item-meta">
                  <span class="reason">{{ item.reason }}</span>
                  <span class="score">推荐度: {{ item.recommendation_score }}%</span>
                </div>
                <div class="item-actions">
                  <el-button type="primary" size="small" @click.stop="startRecommendation(item)">
                    {{ getActionText(item.action) }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 效果评估 -->
      <div class="evaluation-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>学习效果评估</h3>
              <el-button type="text" @click="loadEvaluation">刷新评估</el-button>
            </div>
          </template>
          <div class="evaluation-content">
            <!-- 使用新的学习效果评估组件 -->
            <LearningEvaluation 
              :title="'学习效果评估'"
              :user-id="'current-user'"
            />
          </div>
        </el-card>
      </div>

      <!-- 学习进度分析区域 -->
      <div class="progress-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>学习进度分析</h3>
              <el-button type="text" @click="loadLearningProgress">刷新进度</el-button>
            </div>
          </template>
          <div class="progress-content">
            <!-- 使用新的学习进度图表组件 -->
            <ProgressChart 
              :title="'学习进度趋势'"
              :data="progressChartData"
            />
          </div>
        </el-card>
      </div>
      <div class="trajectory-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>学习轨迹分析</h3>
              <el-button type="text" @click="loadTrajectoryAnalysis">刷新分析</el-button>
            </div>
          </template>
          <div class="trajectory-content">
            <div v-if="trajectoryData" class="trajectory-analysis">
              <!-- 使用新的时间线组件 -->
              <LearningTimeline 
                :title="'学习活动时间线'"
                :user-id="'current-user'"
              />
              
              <!-- 原有的分析数据展示 -->
              <el-row :gutter="20" style="margin-top: 30px;">
                <el-col :span="8">
                  <div class="analysis-item">
                    <h4>学习习惯</h4>
                    <p>学习频率: {{ trajectoryData.learning_habits?.study_frequency || 0 }} 天</p>
                    <p>学习连续性: {{ trajectoryData.learning_habits?.consistency_score || 0 }}%</p>
                    <p>最长连续学习: {{ trajectoryData.learning_habits?.study_streak || 0 }} 天</p>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-item">
                    <h4>学习模式</h4>
                    <p>学习风格: {{ getLearningStyleName(trajectoryData.learning_patterns?.learning_style) }}</p>
                    <p>交互模式: {{ getInteractionPatternName(trajectoryData.learning_patterns?.interaction_pattern) }}</p>
                    <p>学习深度: {{ getLearningDepthName(trajectoryData.learning_patterns?.learning_depth) }}</p>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-item">
                    <h4>学习效率</h4>
                    <p>效率分数: {{ trajectoryData.learning_efficiency?.efficiency_score || 0 }}%</p>
                    <p>进度率: {{ trajectoryData.learning_efficiency?.progress_rate || 0 }}%</p>
                    <p>知识保持率: {{ trajectoryData.learning_efficiency?.knowledge_retention || 0 }}%</p>
                  </div>
                </el-col>
              </el-row>
            </div>
            <div v-else class="empty-state">
              <el-empty description="暂无学习轨迹数据">
                <el-button type="primary" @click="loadTrajectoryAnalysis">开始分析</el-button>
              </el-empty>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 知识点掌握度分析区域 -->
      <div class="mastery-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>知识点掌握度分析</h3>
              <el-button type="text" @click="loadMasteryAnalysis">刷新分析</el-button>
            </div>
          </template>
          <div class="mastery-content">
            <div v-if="masteryData" class="mastery-analysis">
              <div class="mastery-summary">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="summary-item">
                      <h4>总体掌握度</h4>
                      <div class="score-display">
                        {{ masteryData.mastery_report?.summary?.overall_mastery || 0 }}%
                      </div>
                      <p>{{ getMasteryLevelName(masteryData.mastery_report?.summary?.mastery_level) }}</p>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="summary-item">
                      <h4>知识点总数</h4>
                      <div class="score-display">
                        {{ masteryData.mastery_report?.summary?.total_knowledge_points || 0 }}
                      </div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="summary-item">
                      <h4>优势领域</h4>
                      <div class="areas-list">
                        <el-tag v-for="area in masteryData.mastery_report?.summary?.strongest_areas" 
                                :key="area" type="success" style="margin: 2px;">
                          {{ area }}
                        </el-tag>
                      </div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="summary-item">
                      <h4>需要加强</h4>
                      <div class="areas-list">
                        <el-tag v-for="area in masteryData.mastery_report?.summary?.weakest_areas" 
                                :key="area" type="warning" style="margin: 2px;">
                          {{ area }}
                        </el-tag>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
            <div v-else class="empty-state">
              <el-empty description="暂无掌握度分析数据">
                <el-button type="primary" @click="loadMasteryAnalysis">开始分析</el-button>
              </el-empty>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 思维导图区域 -->
      <div class="mindmap-section" v-if="selectedKnowledgeBase">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>知识库思维导图</h3>
              <el-tag type="info">{{ selectedKnowledgeBase.title }}</el-tag>
            </div>
          </template>
          <div class="mindmap-content">
            <MindMapVisualization 
              :knowledge-base-id="selectedKnowledgeBase.id"
            />
          </div>
        </el-card>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import api from '@/utils/api'
import MindMapVisualization from '@/components/MindMapVisualization.vue'
import RadarChart from '@/components/RadarChart.vue'
import LearningTimeline from '@/components/LearningTimeline.vue'
import ProgressChart from '@/components/ProgressChart.vue'
import LearningEvaluation from '@/components/LearningEvaluation.vue'

const router = useRouter()

// 内容统计数据
const learningStats = reactive({
  totalCourses: 0,
  avgProgress: 0,
  totalHours: 0,
  avgScore: 0
})

// 内容进度数据
const learningProgress = ref([])

// 选中的知识库（用于思维导图）
const selectedKnowledgeBase = ref(null)

// 内容轨迹分析数据
const trajectoryData = ref(null)

// 知识点掌握度分析数据
const masteryData = ref(null)

// 推荐内容数据
const recommendations = ref([])

// 效果评估数据
const evaluationData = ref(null)

// 雷达图数据
const radarData = computed(() => {
  if (!evaluationData.value) return []
  
  return [
    { name: '理解能力', value: evaluationData.value.understanding || 0 },
    { name: '应用能力', value: evaluationData.value.application || 0 },
    { name: '分析能力', value: evaluationData.value.analysis || 0 },
    { name: '综合能力', value: evaluationData.value.synthesis || 0 }
  ]
})

// 进度图表数据
const progressChartData = computed(() => {
  if (!learningProgress.value || !learningProgress.value.length) return []
  
  return learningProgress.value.map((progress, index) => ({
    name: progress.knowledge_base_title,
    progress: progress.progress_percentage,
    questions: progress.questions_asked,
    time: progress.time_spent_minutes,
    content: progress.content_generated,
    date: new Date(Date.now() - (learningProgress.value.length - index) * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  }))
})

// 加载内容统计数据
const loadLearningStats = async () => {
  try {
    const response = await api.get('/learning/analytics/stats/')
    Object.assign(learningStats, response.data)
  } catch (error) {
    console.error('加载内容统计失败:', error)
  }
}

// 加载内容进度
const loadLearningProgress = async () => {
  try {
    // 加载知识库学习进度
    const response = await api.get('/learning/knowledge-analytics/')
    learningProgress.value = response.data.knowledge_bases || []
  } catch (error) {
    console.error('加载内容进度失败:', error)
  }
}

// 加载推荐内容
const loadRecommendations = async () => {
  try {
    const response = await api.get('/learning/recommendations/')
    recommendations.value = response.data.recommendations || []
    
    // 检查是否是降级模式
    if (response.data.fallback) {
      ElMessage.warning('推荐服务暂时不可用，已启用降级模式')
    }
  } catch (error) {
    console.error('加载推荐内容失败:', error)
    ElMessage.error('加载推荐内容失败')
  }
}

// 加载效果评估
const loadEvaluation = async () => {
  try {
    const response = await api.get('/learning/evaluation/')
    evaluationData.value = response.data
    
    // 检查是否是降级模式
    if (response.data.fallback) {
      ElMessage.warning('评估服务暂时不可用，已启用降级模式')
    }
  } catch (error) {
    console.error('加载效果评估失败:', error)
    ElMessage.error('加载效果评估失败')
  }
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([
    loadLearningStats(),
    loadLearningProgress(),
    loadRecommendations(),
    loadEvaluation(),
    loadTrajectoryAnalysis(),
    loadMasteryAnalysis()
  ])
  ElMessage.success('数据已刷新')
}

// 加载内容轨迹分析
const loadTrajectoryAnalysis = async () => {
  try {
    const response = await api.get('/learning/trajectory-analysis/')
    trajectoryData.value = response.data.trajectory_analysis
  } catch (error) {
    console.error('加载内容轨迹分析失败:', error)
  }
}

// 加载知识点掌握度分析
const loadMasteryAnalysis = async () => {
  try {
    const response = await api.get('/learning/mastery-analysis/')
    masteryData.value = response.data.mastery_analysis
  } catch (error) {
    console.error('加载掌握度分析失败:', error)
  }
}

// 导出内容报告
const exportReport = async (format: string) => {
  try {
    const response = await api.get(`/learning/export-report/?format=${format}&type=comprehensive`, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `learning_report_${new Date().toISOString().slice(0, 10)}.${format}`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`${format.toUpperCase()}报告导出成功`)
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出报告失败')
  }
}

// 获取内容风格名称
const getLearningStyleName = (style: string) => {
  const styleNames = {
    'inquiry_based': '探究式学习',
    'content_creation': '内容创作式学习',
    'conversational': '对话式学习',
    'unknown': '未知'
  }
  return styleNames[style] || '未知'
}

// 获取交互模式名称
const getInteractionPatternName = (pattern: string) => {
  const patternNames = {
    'deep_dive': '深度探索',
    'moderate': '中等交互',
    'quick_questions': '快速问答',
    'unknown': '未知'
  }
  return patternNames[pattern] || '未知'
}

// 获取内容深度名称
const getLearningDepthName = (depth: string) => {
  const depthNames = {
    'deep': '深度学习',
    'moderate': '中等深度',
    'shallow': '浅层学习'
  }
  return depthNames[depth] || '浅层学习'
}

// 获取掌握等级名称
const getMasteryLevelName = (level: string) => {
  const levelNames = {
    'expert': '专家级',
    'proficient': '熟练级',
    'intermediate': '中级',
    'beginner': '初级',
    'novice': '新手级'
  }
  return levelNames[level] || '新手级'
}

// 生成推荐内容
const generateRecommendations = async () => {
  try {
    await loadRecommendations()
    ElMessage.success('推荐内容已刷新')
  } catch (error) {
    ElMessage.error('生成推荐内容失败')
  }
}

// 生成评估报告
const generateEvaluation = async () => {
  try {
    await loadEvaluation()
    ElMessage.success('评估报告已刷新')
  } catch (error) {
    ElMessage.error('生成评估报告失败')
  }
}

// 查看课程详情
const viewCourseDetail = (courseId: string) => {
  router.push(`/courses/${courseId}`)
}

// 查看知识库详情
const viewKnowledgeBaseDetail = (knowledgeBaseId: string) => {
  // 设置选中的知识库用于思维导图显示
  const progress = learningProgress.value.find(p => p.id === knowledgeBaseId)
  if (progress) {
    selectedKnowledgeBase.value = {
      id: knowledgeBaseId,
      title: progress.title
    }
  }
  router.push(`/knowledge/${knowledgeBaseId}`)
}

// 查看推荐内容
const viewRecommendation = (item: any) => {
  // 根据推荐类型跳转到不同页面
  if (item.type === 'course') {
    router.push(`/courses/${item.id}`)
  } else if (item.type === 'knowledge') {
    router.push(`/knowledge/${item.id}`)
  }
}

// 开始推荐内容
const startRecommendation = (item: any) => {
  viewRecommendation(item)
}

// 开始内容
const startLearning = () => {
  router.push('/courses')
}

// 查看全部进度
const viewAllProgress = () => {
  // 可以跳转到详细的进度页面
  ElMessage.info('跳转到详细进度页面')
}

// 刷新推荐
const refreshRecommendations = () => {
  generateRecommendations()
}

// 获取推荐类型名称
const getRecommendationTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'knowledge_base': '知识库',
    'content_generation': '内容生成',
    'suggestion': '建议',
    'course': '课程'
  }
  return typeMap[type] || type
}

// 获取推荐类型标签样式
const getRecommendationType = (type: string) => {
  const typeMap: Record<string, string> = {
    'knowledge_base': 'primary',
    'content_generation': 'success',
    'suggestion': 'info',
    'course': 'warning'
  }
  return typeMap[type] || 'default'
}

// 获取操作按钮文本
const getActionText = (action: string) => {
  const actionMap: Record<string, string> = {
    'ask_questions': '开始提问',
    'generate_content': '生成内容',
    'explore_features': '探索功能',
    'ask_more_questions': '多提问',
    'explore_topics': '探索主题',
    'start_learning': '开始学习'
  }
  return actionMap[action] || '开始学习'
}

// 工具函数
const getDifficultyName = (level: number) => {
  const names = ['', '初级', '中级', '高级', '专家']
  return names[level] || '未知'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.learning-analytics-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
}

.learning-analytics-container::before {
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
.analytics-header {
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

.header-content h2 {
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

/* Main Content */
.analytics-main {
  padding: 2rem;
  position: relative;
  z-index: 5;
}

/* Overview Section */
.overview-section {
  margin-bottom: 2rem;
}

.overview-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.learning-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.progress-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.time-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.score-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.card-info h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
}

.card-info p {
  color: #6c757d;
  margin: 0;
  font-size: 0.9rem;
}

/* Section Cards */
.section-card {
  margin-bottom: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
}

/* Progress Section */
.progress-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.progress-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.course-info h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.course-info p {
  margin: 0 0 0.75rem 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.course-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #999;
}

.progress-info {
  text-align: right;
  min-width: 200px;
}

.progress-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.progress-text {
  font-weight: 600;
  color: #2c3e50;
  min-width: 40px;
}

.progress-stats {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #6c757d;
}

/* Recommendation Section */
.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.recommendation-item {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.item-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1rem;
  flex: 1;
}

.item-description {
  margin: 0 0 1rem 0;
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.5;
}

.item-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 1rem;
}

.item-actions {
  text-align: right;
}

/* Evaluation Section */
.evaluation-dashboard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.radar-chart h4,
.learning-suggestions h4,
.learning-timeline h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.radar-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.radar-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.radar-label {
  min-width: 80px;
  font-size: 0.9rem;
  color: #6c757d;
}

.radar-value {
  min-width: 40px;
  font-weight: 600;
  color: #2c3e50;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #6c757d;
}

.suggestion-icon {
  color: #f39c12;
  margin-top: 0.125rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

/* 思维导图区域 */
.mindmap-section {
  margin-top: 2rem;
}

.mindmap-content {
  min-height: 500px;
}

/* 学习轨迹分析区域 */
.trajectory-section {
  margin-top: 2rem;
}

.trajectory-analysis {
  padding: 20px 0;
}

.analysis-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.analysis-item h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 16px;
}

.analysis-item p {
  color: #6c757d;
  margin: 8px 0;
  font-size: 14px;
}

/* 知识点掌握度分析区域 */
.mastery-section {
  margin-top: 2rem;
}

.mastery-analysis {
  padding: 20px 0;
}

.mastery-summary {
  margin-bottom: 20px;
}

.summary-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.summary-item h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 16px;
}

.score-display {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.areas-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 5px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .evaluation-dashboard {
    grid-template-columns: 1fr;
  }
  
  .recommendation-grid {
    grid-template-columns: 1fr;
  }
  
  .progress-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .progress-info {
    text-align: left;
    width: 100%;
  }
}
</style>
