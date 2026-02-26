<template>
  <div class="course-analytics">
    <el-card class="analytics-card">
      <template #header>
        <div class="card-header">
          <h3>学习分析</h3>
          <el-button @click="refreshAnalytics" :loading="loading" size="small" class="ghost-btn">
            <AppleIcon name="arrow.clockwise" :size="14" />
            刷新
          </el-button>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="analytics" class="analytics-content">
        <!-- 总体进度 -->
        <div class="progress-section">
          <h4>总体进度</h4>
          <div class="progress-stats">
            <div class="stat-item">
              <div class="stat-label">完成进度</div>
              <el-progress 
                :percentage="analytics.overall_progress" 
                :stroke-width="12"
                :color="getProgressColor(analytics.overall_progress)"
              />
            </div>
            <div class="stat-item">
              <div class="stat-label">学习时间</div>
              <div class="stat-value">{{ formatTime(analytics.total_time_spent) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">完成章节</div>
              <div class="stat-value">{{ analytics.completed_chapters }}/{{ analytics.total_chapters }}</div>
            </div>
          </div>
        </div>
        
        <!-- 章节进度 -->
        <div class="chapters-section">
          <h4>章节进度</h4>
          <div class="chapters-progress">
            <div 
              v-for="chapter in analytics.chapter_progress" 
              :key="chapter.id"
              class="chapter-progress-item"
            >
              <div class="chapter-info">
                <span class="chapter-title">{{ chapter.title }}</span>
                <span class="chapter-time">{{ formatTime(chapter.time_spent) }}</span>
              </div>
              <el-progress 
                :percentage="chapter.progress" 
                :stroke-width="8"
                :color="getProgressColor(chapter.progress)"
              />
            </div>
          </div>
        </div>
        
        <!-- 学习趋势 -->
        <div class="trends-section">
          <h4>学习趋势</h4>
          <div class="trends-chart">
            <div class="chart-placeholder">
              <AppleIcon name="chart.xyaxis.line" :size="48" />
              <p>学习趋势图表</p>
              <small>显示每日学习时间和进度变化</small>
            </div>
          </div>
        </div>
        
        <!-- 知识点掌握 -->
        <div class="knowledge-section">
          <h4>知识点掌握情况</h4>
          <div class="knowledge-stats">
            <div class="knowledge-item">
              <span class="knowledge-label">已掌握</span>
              <el-tag type="success">{{ analytics.mastered_concepts || 0 }}个</el-tag>
            </div>
            <div class="knowledge-item">
              <span class="knowledge-label">学习中</span>
              <el-tag type="warning">{{ analytics.learning_concepts || 0 }}个</el-tag>
            </div>
            <div class="knowledge-item">
              <span class="knowledge-label">未开始</span>
              <el-tag type="info">{{ analytics.pending_concepts || 0 }}个</el-tag>
            </div>
          </div>
        </div>
        
        <!-- 学习建议 -->
        <div class="suggestions-section">
          <h4>学习建议</h4>
          <div class="suggestions-list">
            <div 
              v-for="suggestion in analytics.suggestions" 
              :key="suggestion.id"
              class="suggestion-item"
            >
              <div class="suggestion-icon" :style="{ background: getSuggestionGradient(suggestion.type) }">
                <AppleIcon :name="getSuggestionIcon(suggestion.type)" :size="16" />
              </div>
              <span>{{ suggestion.content }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <el-empty description="暂无学习数据">
          <el-button type="primary" @click="startLearning">开始学习</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import api from '@/utils/api'

interface ChapterProgress {
  id: string
  title: string
  progress: number
  time_spent: number
  completed: boolean
}

interface Analytics {
  overall_progress: number
  total_time_spent: number
  completed_chapters: number
  total_chapters: number
  chapter_progress: ChapterProgress[]
  mastered_concepts: number
  learning_concepts: number
  pending_concepts: number
  suggestions: Array<{
    id: string
    type: 'success' | 'warning' | 'info'
    content: string
  }>
}

const props = defineProps<{
  courseId: string
}>()

const analytics = ref<Analytics | null>(null)
const loading = ref(false)

const loadAnalytics = async () => {
  try {
    loading.value = true
    const response = await api.get(`/learning/analytics/${props.courseId}/`)
    analytics.value = response.data
  } catch (error) {
    console.error('加载学习分析失败:', error)
    ElMessage.error('加载学习分析失败')
  } finally {
    loading.value = false
  }
}

const refreshAnalytics = () => {
  loadAnalytics()
}

const formatTime = (minutes: number) => {
  if (minutes < 60) {
    return `${minutes}分钟`
  } else {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}小时${mins}分钟`
  }
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 80) return '#34C759'
  if (percentage >= 60) return '#0A84FF'
  if (percentage >= 40) return '#FF9F0A'
  return '#8E8E93'
}

const getSuggestionIcon = (type: string) => {
  switch (type) {
    case 'success': return 'checkmark.circle'
    case 'warning': return 'exclamationmark.triangle'
    case 'info': return 'clock'
    default: return 'info.circle'
  }
}

const getSuggestionGradient = (type: string) => {
  const map: Record<string, string> = {
    success: 'linear-gradient(135deg, #34C759, #81FBB8)',
    warning: 'linear-gradient(135deg, #FF9F0A, #FFD60A)',
    info: 'linear-gradient(135deg, #0A84FF, #5AC8FA)'
  }
  return map[type] || 'linear-gradient(135deg, #8E8E93, #C7C7CC)'
}

const startLearning = () => {
  // 跳转到课程学习页面
  window.location.href = `/courses/${props.courseId}`
}

onMounted(() => {
  loadAnalytics()
})
</script>

<style scoped>
.course-analytics {
  width: 100%;
  background: var(--apple-background);
  border-radius: 32px;
  padding: 24px 32px;
  border: var(--apple-border);
}

.analytics-card {
  margin-bottom: 20px;
  border-radius: 24px;
  border: var(--apple-border);
  background: var(--apple-surface);
  box-shadow: var(--apple-card-shadow);
}

.analytics-card :deep(.el-card__header) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.analytics-card :deep(.el-card__body) {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: var(--apple-text-primary);
}

:deep(.ghost-btn.el-button) {
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.9);
  color: var(--apple-text-primary);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
}

:deep(.ghost-btn.el-button:hover) {
  background: #f2f2f7;
}

.loading-container {
  padding: 20px;
}

.analytics-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-section,
.chapters-section,
.trends-section,
.knowledge-section,
.suggestions-section {
  padding: 20px;
  background: var(--apple-elevated);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.progress-section h4,
.chapters-section h4,
.trends-section h4,
.knowledge-section h4,
.suggestions-section h4 {
  margin: 0 0 16px 0;
  color: var(--apple-text-primary);
  font-size: 16px;
}

.progress-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  color: var(--apple-text-secondary);
  font-size: 14px;
}

.stat-value {
  color: var(--apple-text-primary);
  font-weight: 600;
  font-size: 18px;
}

.chapters-progress {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chapter-progress-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-title {
  color: var(--apple-text-primary);
  font-weight: 500;
}

.chapter-time {
  color: var(--apple-text-tertiary);
  font-size: 12px;
}

.trends-chart {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  background: var(--apple-surface);
}

.chart-placeholder {
  text-align: center;
  color: var(--apple-text-tertiary);
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.chart-placeholder p {
  margin: 8px 0 4px 0;
  font-size: 16px;
}

.chart-placeholder small {
  font-size: 12px;
}

.knowledge-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.knowledge-label {
  color: var(--apple-text-secondary);
  font-size: 14px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--apple-surface);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: var(--apple-card-shadow);
}

.suggestion-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

@media (max-width: 768px) {
  .progress-stats {
    gap: 12px;
  }
  
  .knowledge-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .chapter-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
