<!-- 学习轨迹时间线组件 -->
<template>
  <div class="timeline-container">
    <div class="timeline-header">
      <h3>{{ title }}</h3>
      <div class="timeline-controls">
        <el-select v-model="selectedPeriod" @change="handlePeriodChange" size="small">
          <el-option label="最近7天" value="7"></el-option>
          <el-option label="最近30天" value="30"></el-option>
          <el-option label="最近90天" value="90"></el-option>
        </el-select>
        <el-button @click="refreshData" size="small" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="timeline-content">
      <div v-if="loading" class="loading-container">
        <el-loading-spinner />
        <p>正在加载学习轨迹...</p>
      </div>
      
      <div v-else-if="error" class="error-container">
        <el-alert :title="error" type="error" :closable="false" show-icon />
        <el-button @click="refreshData" style="margin-top: 20px;">
          重新加载
        </el-button>
      </div>
      
      <div v-else-if="timelineData.length === 0" class="empty-container">
        <el-empty description="暂无学习轨迹数据">
          <el-button type="primary" @click="refreshData">开始学习</el-button>
        </el-empty>
      </div>
      
      <div v-else class="timeline-visualization">
        <!-- 统计概览 -->
        <div class="timeline-stats">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalDays }}</div>
                <div class="stat-label">学习天数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalHours }}</div>
                <div class="stat-label">学习时长(小时)</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalQuestions }}</div>
                <div class="stat-label">提问次数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.avgProgress }}</div>
                <div class="stat-label">平均进度(%)</div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 时间线图表 -->
        <div ref="chartRef" class="timeline-chart"></div>
        
        <!-- 学习里程碑 -->
        <div class="milestones-section">
          <h4>学习里程碑</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(milestone, index) in milestones"
              :key="index"
              :timestamp="milestone.date"
              :type="milestone.type"
              :icon="milestone.icon"
            >
              <h4>{{ milestone.title }}</h4>
              <p>{{ milestone.description }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

interface TimelineData {
  date: string
  questions: number
  progress: number
  timeSpent: number
  contentGenerated: number
}

interface Milestone {
  date: string
  title: string
  description: string
  type: string
  icon?: string
}

interface Props {
  userId?: string
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '学习轨迹分析'
})

// 响应式数据
const loading = ref(false)
const error = ref('')
const selectedPeriod = ref('30')
const timelineData = ref<TimelineData[]>([])
const milestones = ref<Milestone[]>([])
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 统计数据
const stats = reactive({
  totalDays: 0,
  totalHours: 0,
  totalQuestions: 0,
  avgProgress: 0
})

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chartInstance || !timelineData.value.length) return

  const dates = timelineData.value.map(item => item.date)
  const questions = timelineData.value.map(item => item.questions)
  const progress = timelineData.value.map(item => item.progress)
  const timeSpent = timelineData.value.map(item => item.timeSpent)

  const option = {
    title: {
      text: '学习活动趋势',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['提问次数', '学习进度', '学习时长(分钟)'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '提问次数',
        position: 'left',
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '学习进度(%)',
        position: 'right',
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '提问次数',
        type: 'line',
        yAxisIndex: 0,
        data: questions,
        smooth: true,
        lineStyle: {
          color: '#409eff'
        },
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(64, 158, 255, 0.3)'
            }, {
              offset: 1, color: 'rgba(64, 158, 255, 0.1)'
            }]
          }
        }
      },
      {
        name: '学习进度',
        type: 'line',
        yAxisIndex: 1,
        data: progress,
        smooth: true,
        lineStyle: {
          color: '#67c23a'
        },
        itemStyle: {
          color: '#67c23a'
        }
      },
      {
        name: '学习时长',
        type: 'bar',
        yAxisIndex: 0,
        data: timeSpent,
        itemStyle: {
          color: '#e6a23c'
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 加载数据
const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await api.get('/learning/trajectory-analysis/', {
      params: { days: selectedPeriod.value }
    })
    
    const trajectoryData = response.data.trajectory_analysis
    
    // 处理时间线数据
    timelineData.value = processTimelineData(trajectoryData)
    
    // 处理里程碑数据
    milestones.value = processMilestones(trajectoryData)
    
    // 更新统计数据
    updateStats(trajectoryData)
    
    // 更新图表
    nextTick(() => {
      updateChart()
    })
    
  } catch (err) {
    console.error('加载学习轨迹失败:', err)
    error.value = err.response?.data?.error || '加载学习轨迹失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 处理时间线数据
const processTimelineData = (data: any): TimelineData[] => {
  const dailyPattern = data.time_distribution?.daily_pattern || {}
  const processedData: TimelineData[] = []
  
  // 生成最近N天的数据
  const days = parseInt(selectedPeriod.value)
  const today = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    
    processedData.push({
      date: dateStr,
      questions: Math.floor(Math.random() * 10), // 模拟数据
      progress: Math.min(100, Math.random() * 100),
      timeSpent: Math.floor(Math.random() * 120),
      contentGenerated: Math.floor(Math.random() * 5)
    })
  }
  
  return processedData
}

// 处理里程碑数据
const processMilestones = (data: any): Milestone[] => {
  const milestones: Milestone[] = []
  
  // 基于学习数据生成里程碑
  if (data.learning_efficiency?.efficiency_score > 80) {
    milestones.push({
      date: new Date().toISOString().split('T')[0],
      title: '高效学习成就',
      description: '您的学习效率达到了优秀水平！',
      type: 'success',
      icon: 'Trophy'
    })
  }
  
  if (data.learning_habits?.study_streak > 7) {
    milestones.push({
      date: new Date().toISOString().split('T')[0],
      title: '连续学习达人',
      description: `您已经连续学习${data.learning_habits.study_streak}天！`,
      type: 'primary',
      icon: 'Calendar'
    })
  }
  
  return milestones
}

// 更新统计数据
const updateStats = (data: any) => {
  stats.totalDays = data.learning_habits?.study_frequency || 0
  stats.totalHours = (data.time_distribution?.total_study_time || 0) / 60
  stats.totalQuestions = timelineData.value.reduce((sum, item) => sum + item.questions, 0)
  stats.avgProgress = timelineData.value.reduce((sum, item) => sum + item.progress, 0) / timelineData.value.length || 0
}

// 处理时间段变化
const handlePeriodChange = () => {
  loadData()
}

// 刷新数据
const refreshData = () => {
  loadData()
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
  initChart()
})

// 组件卸载时销毁图表
const destroyChart = () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

// 导出方法
defineExpose({
  refresh: refreshData,
  destroy: destroyChart
})
</script>

<style scoped>
.timeline-container {
  width: 100%;
  height: 100%;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.timeline-header h3 {
  margin: 0;
  color: #303133;
}

.timeline-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.timeline-content {
  padding: 20px;
  background: #f5f7fa;
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

.timeline-visualization {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.timeline-stats {
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
}

.timeline-chart {
  width: 100%;
  height: 400px;
  margin-bottom: 30px;
}

.milestones-section {
  margin-top: 30px;
}

.milestones-section h4 {
  margin-bottom: 20px;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .timeline-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .timeline-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .timeline-stats .el-row {
    margin: 0 -10px;
  }
  
  .timeline-stats .el-col {
    padding: 0 10px;
    margin-bottom: 16px;
  }
}
</style>
