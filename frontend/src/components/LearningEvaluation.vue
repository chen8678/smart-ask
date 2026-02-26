<!-- 学习效果评估组件 -->
<template>
  <div class="evaluation-container">
    <div class="evaluation-header">
      <h3>{{ title }}</h3>
      <div class="evaluation-controls">
        <el-button @click="generateEvaluation" type="primary" :loading="generating" class="ghost-btn">
          <AppleIcon name="document" :size="16" />
          生成评估报告
        </el-button>
        <el-button @click="refreshData" :loading="loading" class="ghost-btn">
          <AppleIcon name="refresh" :size="16" />
          刷新数据
        </el-button>
      </div>
    </div>
    
    <div class="evaluation-content">
      <div v-if="loading" class="loading-container">
        <el-loading-spinner />
        <p>正在加载评估数据...</p>
      </div>
      
      <div v-else-if="error" class="error-container">
        <el-alert :title="error" type="error" :closable="false" show-icon />
        <el-button @click="refreshData" style="margin-top: 20px;">
          重新加载
        </el-button>
      </div>
      
      <div v-else-if="!evaluationData" class="empty-container">
        <el-empty description="暂无学习效果评估数据">
          <el-button type="primary" @click="generateEvaluation">开始评估</el-button>
        </el-empty>
      </div>
      
      <div v-else class="evaluation-dashboard">
        <!-- 总体评分 -->
        <div class="overall-score">
          <div class="score-circle">
            <div class="score-value">{{ overallScore }}</div>
            <div class="score-label">综合评分</div>
          </div>
          <div class="score-breakdown">
            <div class="score-item">
              <span class="score-name">理解能力</span>
              <el-progress 
                :percentage="evaluationData.understanding" 
                :stroke-width="8"
                :show-text="false"
                color="#0A84FF"
              />
              <span class="score-percentage">{{ evaluationData.understanding }}%</span>
            </div>
            <div class="score-item">
              <span class="score-name">应用能力</span>
              <el-progress 
                :percentage="evaluationData.application" 
                :stroke-width="8"
                :show-text="false"
                color="#34C759"
              />
              <span class="score-percentage">{{ evaluationData.application }}%</span>
            </div>
            <div class="score-item">
              <span class="score-name">分析能力</span>
              <el-progress 
                :percentage="evaluationData.analysis" 
                :stroke-width="8"
                :show-text="false"
                color="#FF9F0A"
              />
              <span class="score-percentage">{{ evaluationData.analysis }}%</span>
            </div>
            <div class="score-item">
              <span class="score-name">综合能力</span>
              <el-progress 
                :percentage="evaluationData.synthesis" 
                :stroke-width="8"
                :show-text="false"
                color="#AF52DE"
              />
              <span class="score-percentage">{{ evaluationData.synthesis }}%</span>
            </div>
          </div>
        </div>
        
        <!-- 能力雷达图 -->
        <div class="radar-section">
          <h4>能力分析雷达图</h4>
          <div class="radar-container">
            <RadarChart 
              :data="radarData"
              :title="'学习能力雷达图'"
              :width="400"
              :height="300"
            />
          </div>
        </div>
        
        <!-- 学习建议 -->
        <div class="suggestions-section">
          <h4>学习建议</h4>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in evaluationData.suggestions" 
              :key="index"
              class="suggestion-item"
            >
              <div class="suggestion-header">
                <el-tag :type="getSuggestionType(suggestion.type)" size="small">
                  {{ suggestion.type }}
                </el-tag>
                <span class="suggestion-title">{{ suggestion.title }}</span>
              </div>
              <div class="suggestion-content">
                {{ suggestion.content }}
              </div>
              <div class="suggestion-actions">
                <el-button size="small" type="text" @click="applySuggestion(suggestion)">
                  应用建议
                </el-button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 学习轨迹分析 -->
        <div class="trajectory-section">
          <h4>学习轨迹分析</h4>
          <div class="trajectory-analysis">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="analysis-item">
                  <h5>学习效率</h5>
                  <div class="analysis-value">{{ evaluationData.efficiency || 0 }}%</div>
                  <div class="analysis-desc">整体学习效率</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="analysis-item">
                  <h5>知识保持率</h5>
                  <div class="analysis-value">{{ evaluationData.retention || 0 }}%</div>
                  <div class="analysis-desc">知识记忆保持率</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="analysis-item">
                  <h5>学习深度</h5>
                  <div class="analysis-value">{{ evaluationData.depth || 0 }}%</div>
                  <div class="analysis-desc">学习内容深度</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import RadarChart from '@/components/RadarChart.vue'
import api from '@/utils/api'

interface EvaluationData {
  understanding: number
  application: number
  analysis: number
  synthesis: number
  efficiency: number
  retention: number
  depth: number
  suggestions: Array<{
    type: string
    title: string
    content: string
  }>
}

interface Props {
  title?: string
  userId?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '学习效果评估',
  userId: 'current-user'
})

// 响应式数据
const loading = ref(false)
const generating = ref(false)
const error = ref('')
const evaluationData = ref<EvaluationData | null>(null)

// 计算总体评分
const overallScore = computed(() => {
  if (!evaluationData.value) return 0
  
  const scores = [
    evaluationData.value.understanding,
    evaluationData.value.application,
    evaluationData.value.analysis,
    evaluationData.value.synthesis
  ]
  
  return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length)
})

// 雷达图数据
const radarData = computed(() => {
  if (!evaluationData.value) return []
  
  return [
    { name: '理解能力', value: evaluationData.value.understanding },
    { name: '应用能力', value: evaluationData.value.application },
    { name: '分析能力', value: evaluationData.value.analysis },
    { name: '综合能力', value: evaluationData.value.synthesis }
  ]
})

// 获取建议类型颜色
const getSuggestionType = (type: string) => {
  const typeMap = {
    '理解': 'primary',
    '应用': 'success',
    '分析': 'warning',
    '综合': 'info',
    '效率': 'danger'
  }
  return typeMap[type as keyof typeof typeMap] || 'default'
}

// 应用建议
const applySuggestion = (suggestion: any) => {
  ElMessage.success(`已应用建议：${suggestion.title}`)
  // 这里可以添加具体的应用逻辑
}

// 生成评估报告
const generateEvaluation = async () => {
  generating.value = true
  error.value = ''
  
  try {
    const response = await api.post('/learning/evaluation/', {
      user_id: props.userId,
      evaluation_type: 'comprehensive'
    })
    
    evaluationData.value = response.data.evaluation
    
    ElMessage.success('学习效果评估报告生成成功')
    
  } catch (err) {
    console.error('生成学习效果评估失败:', err)
    error.value = err.response?.data?.error || '生成学习效果评估失败'
    ElMessage.error(error.value)
  } finally {
    generating.value = false
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await api.get('/learning/evaluation/', {
      params: { user_id: props.userId }
    })
    
    evaluationData.value = response.data.evaluation
    
  } catch (err) {
    console.error('加载学习效果评估失败:', err)
    error.value = err.response?.data?.error || '加载学习效果评估失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.evaluation-container {
  width: 100%;
  height: 100%;
  background: var(--apple-background);
  border-radius: 32px;
  padding: 24px 32px;
  border: var(--apple-border);
  backdrop-filter: blur(24px);
}

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: var(--apple-surface);
  border: var(--apple-border);
  border-radius: 24px;
  margin-bottom: 24px;
  box-shadow: var(--apple-card-shadow);
}

.evaluation-header h3 {
  margin: 0;
  color: var(--apple-text-primary);
}

.evaluation-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

:deep(.ghost-btn.el-button) {
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.85);
  color: var(--apple-text-primary);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 18px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

:deep(.ghost-btn.el-button.is-loading) {
  opacity: 0.8;
}

:deep(.ghost-btn.el-button:hover) {
  background: #f2f2f7;
}

.evaluation-content {
  padding: 0;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.evaluation-dashboard {
  background: var(--apple-surface);
  border-radius: 24px;
  padding: 24px;
  border: var(--apple-border);
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-shadow: var(--apple-card-shadow);
}

.overall-score {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 24px;
  background: var(--apple-elevated);
  border-radius: 24px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  color: var(--apple-text-primary);
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  border: 0;
  background: conic-gradient(#0a84ff, #30d158, #5e5ce6, #0a84ff);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.score-circle::after {
  content: '';
  position: absolute;
  inset: 10px;
  border-radius: 50%;
  background: var(--apple-surface);
  border: var(--apple-border);
}

.score-circle > * {
  position: relative;
  z-index: 1;
}

.score-value {
  font-size: 40px;
  font-weight: 600;
  margin-bottom: 4px;
}

.score-label {
  font-size: 12px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--apple-text-tertiary);
}

.score-breakdown {
  flex: 1;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.score-name {
  width: 90px;
  font-size: 14px;
  color: var(--apple-text-secondary);
}

.score-percentage {
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
}

.radar-section,
.suggestions-section,
.trajectory-section {
  background: var(--apple-surface);
  border: var(--apple-border);
  border-radius: 24px;
  padding: 24px;
  box-shadow: var(--apple-card-shadow);
}

.radar-section h4,
.suggestions-section h4,
.trajectory-section h4 {
  margin-bottom: 16px;
  color: #1f1f1f;
  font-size: 18px;
}

.radar-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: var(--apple-elevated);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.suggestions-list {
  display: grid;
  gap: 16px;
}

.suggestion-item {
  padding: 20px;
  background: var(--apple-elevated);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.suggestion-title {
  font-weight: 600;
  color: #303133;
}

.suggestion-content {
  color: var(--apple-text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
}

.suggestion-actions {
  text-align: right;
}

.trajectory-analysis {
  background: transparent;
  border-radius: 0;
  padding: 0;
}

.analysis-item {
  text-align: center;
  padding: 20px;
  background: var(--apple-elevated);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.analysis-item h5 {
  margin: 0 0 12px 0;
  color: var(--apple-text-secondary);
  font-size: 16px;
}

.analysis-value {
  font-size: 32px;
  font-weight: 600;
  color: #0a84ff;
  margin-bottom: 8px;
}

.analysis-desc {
  font-size: 14px;
  color: var(--apple-text-tertiary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .evaluation-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .evaluation-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .overall-score {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .score-breakdown {
    width: 100%;
  }
  
  .radar-container {
    padding: 10px;
  }
  
  .trajectory-analysis .el-row {
    margin: 0 -10px;
  }
  
  .trajectory-analysis .el-col {
    padding: 0 10px;
    margin-bottom: 16px;
  }
}
</style>
