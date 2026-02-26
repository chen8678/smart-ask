<!-- 学习进度图表组件 -->
<template>
  <div class="progress-chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <el-select v-model="selectedMetric" @change="handleMetricChange" size="small" class="metric-select">
          <el-option label="学习进度" value="progress"></el-option>
          <el-option label="提问次数" value="questions"></el-option>
          <el-option label="学习时长" value="time"></el-option>
          <el-option label="内容生成" value="content"></el-option>
        </el-select>
        <el-button @click="refreshData" size="small" :loading="loading" class="ghost-btn">
          <AppleIcon name="arrow.clockwise" :size="14" />
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="chart-content">
      <div v-if="loading" class="loading-container">
        <el-loading-spinner />
        <p>正在加载数据...</p>
      </div>
      
      <div v-else-if="error" class="error-container">
        <el-alert :title="error" type="error" :closable="false" show-icon />
        <el-button @click="refreshData" style="margin-top: 20px;">
          重新加载
        </el-button>
      </div>
      
      <div v-else-if="chartData.length === 0" class="empty-container">
        <el-empty description="暂无学习进度数据">
          <el-button type="primary" @click="refreshData">开始学习</el-button>
        </el-empty>
      </div>
      
      <div v-else class="chart-visualization">
        <!-- 图表容器 -->
        <div ref="chartRef" class="progress-chart"></div>
        
        <!-- 统计信息 -->
        <div class="chart-stats">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">总计</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.average }}</div>
                <div class="stat-label">平均值</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.max }}</div>
                <div class="stat-label">最大值</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.trend }}</div>
                <div class="stat-label">趋势</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import AppleIcon from '@/components/AppleIcon.vue'
import api from '@/utils/api'

interface ProgressData {
  name: string
  progress: number
  questions: number
  time: number
  content: number
  date: string
}

interface Props {
  title?: string
  data?: ProgressData[]
  autoRefresh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '学习进度分析',
  autoRefresh: false
})

// 响应式数据
const loading = ref(false)
const error = ref('')
const selectedMetric = ref('progress')
const chartData = ref<ProgressData[]>([])
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const getCssColor = (variable: string, fallback: string) => {
  if (typeof window === 'undefined') {
    return fallback
  }
  const value = getComputedStyle(document.documentElement).getPropertyValue(variable)
  return value?.trim() || fallback
}

const metricColorVars: Record<string, { base: string; soft: string; fallback: [string, string] }> = {
  progress: { base: '--apple-chart-blue', soft: '--apple-chart-blue-soft', fallback: ['#0a84ff', 'rgba(10,132,255,0.18)'] },
  questions: { base: '--apple-chart-green', soft: '--apple-chart-green-soft', fallback: ['#30d158', 'rgba(48,209,88,0.18)'] },
  time: { base: '--apple-chart-orange', soft: '--apple-chart-orange-soft', fallback: ['#ff9500', 'rgba(255,149,0,0.18)'] },
  content: { base: '--apple-chart-purple', soft: '--apple-chart-purple-soft', fallback: ['#bf5af2', 'rgba(191,90,242,0.2)'] }
}

// 统计数据
const stats = reactive({
  total: 0,
  average: 0,
  max: 0,
  trend: '稳定'
})

// 计算当前指标的数据
const currentData = computed(() => {
  if (!chartData.value.length) return []
  
  return chartData.value.map(item => ({
    name: item.name,
    value: item[selectedMetric.value as keyof ProgressData] as number,
    date: item.date
  }))
})

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chartInstance || !currentData.value.length) return

  const data = currentData.value
  const dates = data.map(item => item.date)
  const values = data.map(item => item.value)

  const metricColor = getMetricColor(selectedMetric.value)
  const metricSoftColor = getMetricSoftColor(selectedMetric.value)
  const textColor = getCssColor('--apple-text-primary', '#1f1f1f')
  const secondaryText = getCssColor('--apple-text-tertiary', '#8e8e93')
  const gridColor = getCssColor('--apple-chart-grid', 'rgba(120,120,128,0.25)')
  const gridBackground = getCssColor('--apple-chart-surface', 'rgba(10,10,15,0.05)')

  const option = {
    textStyle: {
      fontFamily: getCssColor('--apple-font-family', 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif'),
      color: textColor
    },
    title: {
      text: getMetricTitle(selectedMetric.value),
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: textColor
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#ffffff',
      borderColor: gridColor,
      textStyle: {
        color: textColor
      },
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: gridColor
        }
      },
      formatter: (params: any) => {
        const datum = params[0]
        return `${datum.name}<br/>${getMetricTitle(selectedMetric.value)}: ${datum.value}${getMetricUnit(selectedMetric.value)}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '18%',
      containLabel: true,
      backgroundColor: gridBackground,
      borderColor: 'transparent'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 32,
        color: secondaryText
      },
      axisLine: {
        lineStyle: { color: gridColor }
      },
      axisTick: {
        lineStyle: { color: gridColor }
      }
    },
    yAxis: {
      type: 'value',
      name: getMetricTitle(selectedMetric.value),
      nameTextStyle: {
        color: secondaryText
      },
      axisLabel: {
        formatter: `{value}${getMetricUnit(selectedMetric.value)}`,
        color: secondaryText
      },
      splitLine: {
        lineStyle: { color: gridColor }
      }
    },
    series: [
      {
        name: getMetricTitle(selectedMetric.value),
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: {
          color: metricColor,
          width: 3
        },
        itemStyle: {
          color: '#ffffff',
          borderColor: metricColor,
          borderWidth: 2
        },
        symbolSize: 6,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: metricSoftColor },
            { offset: 1, color: 'rgba(255,255,255,0)' }
          ])
        },
        markPoint: {
          symbolSize: 48,
          itemStyle: { color: metricColor },
          data: [
            { type: 'max', name: '最大值' },
            { type: 'min', name: '最小值' }
          ]
        },
        markLine: {
          lineStyle: {
            color: gridColor,
            type: 'dashed'
          },
          label: {
            color: secondaryText
          },
          data: [
            { type: 'average', name: '平均值' }
          ]
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 获取指标标题
const getMetricTitle = (metric: string): string => {
  const titles = {
    progress: '学习进度',
    questions: '提问次数',
    time: '学习时长',
    content: '内容生成'
  }
  return titles[metric as keyof typeof titles] || metric
}

// 获取指标单位
const getMetricUnit = (metric: string): string => {
  const units = {
    progress: '%',
    questions: '次',
    time: '分钟',
    content: '次'
  }
  return units[metric as keyof typeof units] || ''
}

// 获取指标颜色
const getMetricColor = (metric: string): string => {
  const config = metricColorVars[metric] || metricColorVars.progress
  return getCssColor(config.base, config.fallback[0])
}

const getMetricSoftColor = (metric: string): string => {
  const config = metricColorVars[metric] || metricColorVars.progress
  return getCssColor(config.soft, config.fallback[1])
}

// 更新统计数据
const updateStats = () => {
  if (!currentData.value.length) return

  const values = currentData.value.map(item => item.value)
  stats.total = values.reduce((sum, val) => sum + val, 0)
  stats.average = Math.round(stats.total / values.length)
  stats.max = Math.max(...values)
  
  // 计算趋势
  if (values.length >= 2) {
    const recent = values.slice(-3).reduce((sum, val) => sum + val, 0) / 3
    const earlier = values.slice(0, 3).reduce((sum, val) => sum + val, 0) / 3
    
    if (recent > earlier * 1.1) {
      stats.trend = '上升'
    } else if (recent < earlier * 0.9) {
      stats.trend = '下降'
    } else {
      stats.trend = '稳定'
    }
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 如果props中有数据，直接使用
    if (props.data && props.data.length > 0) {
      chartData.value = props.data
    } else {
      // 否则从API加载
      const response = await api.get('/learning/knowledge-analytics/')
      const knowledgeBases = response.data.knowledge_bases || []
      
      // 转换为图表数据格式
      chartData.value = knowledgeBases.map((kb: any, index: number) => ({
        name: kb.title,
        progress: kb.progress || 0,
        questions: kb.questions_asked || 0,
        time: kb.time_spent || 0,
        content: kb.content_generated || 0,
        date: new Date(Date.now() - (knowledgeBases.length - index) * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      }))
    }
    
    // 更新统计数据
    updateStats()
    
    // 更新图表
    nextTick(() => {
      updateChart()
    })
    
  } catch (err) {
    console.error('加载学习进度数据失败:', err)
    error.value = err.response?.data?.error || '加载学习进度数据失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
}

// 监听指标变化
const handleMetricChange = () => {
  updateStats()
  nextTick(() => {
    updateChart()
  })
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
  destroy: destroyChart,
  updateMetric: (metric: string) => {
    selectedMetric.value = metric
    handleMetricChange()
  }
})
</script>

<style scoped>
.progress-chart-container {
  width: 100%;
  height: 100%;
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-card-radius);
  background: var(--apple-surface);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px var(--apple-spacing-lg);
  border-bottom: 1px solid var(--apple-border);
}

.chart-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--apple-text-primary);
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.metric-select :deep(.el-input__wrapper) {
  border-radius: var(--apple-pill-radius);
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: var(--apple-elevated);
}

.chart-content {
  padding: var(--apple-spacing-lg);
  background: var(--apple-elevated);
  border-radius: 0 0 var(--apple-card-radius) var(--apple-card-radius);
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 320px;
  gap: 12px;
  color: var(--apple-text-secondary);
}

.chart-visualization {
  background: var(--apple-surface);
  border-radius: 24px;
  border: 1px solid var(--apple-border);
  padding: var(--apple-spacing-lg);
}

.progress-chart {
  width: 100%;
  height: 360px;
  margin-bottom: var(--apple-spacing-lg);
}

.chart-stats {
  margin-top: var(--apple-spacing-md);
}

.stat-item {
  text-align: center;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--apple-border);
  background: var(--apple-elevated);
}

.stat-value {
  font-size: 26px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  color: var(--apple-text-tertiary);
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .chart-controls {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .chart-controls .ghost-btn {
    justify-content: center;
  }

  .chart-stats .el-row {
    margin: 0;
  }

  .chart-stats .el-col {
    margin-bottom: 12px;
  }
}
</style>
