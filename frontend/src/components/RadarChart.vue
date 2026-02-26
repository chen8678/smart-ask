<!-- 雷达图组件 -->
<template>
  <div class="radar-chart-container">
    <div ref="chartRef" class="radar-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

interface RadarData {
  name: string
  value: number
}

interface Props {
  data: RadarData[]
  title?: string
  width?: number
  height?: number
  maxValue?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '能力雷达图',
  width: 400,
  height: 400,
  maxValue: 100
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const getCssColor = (variable: string, fallback: string) => {
  if (typeof window === 'undefined') {
    return fallback
  }
  const value = getComputedStyle(document.documentElement).getPropertyValue(variable)
  return value?.trim() || fallback
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chartInstance || !props.data.length) return

  const primary = getCssColor('--apple-chart-blue', '#0a84ff')
  const primarySoft = getCssColor('--apple-chart-blue-soft', 'rgba(10,132,255,0.18)')
  const gridColor = getCssColor('--apple-chart-grid', 'rgba(120,120,128,0.25)')
  const textColor = getCssColor('--apple-text-primary', '#1f1f1f')

  const option = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: textColor
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}'
    },
    radar: {
      indicator: props.data.map(item => ({
        name: item.name,
        max: props.maxValue
      })),
      radius: '70%',
      splitNumber: 5,
      splitArea: {
        areaStyle: {
          color: [
            'rgba(10, 132, 255, 0.04)',
            'rgba(10, 132, 255, 0.08)',
            'rgba(10, 132, 255, 0.12)',
            'rgba(10, 132, 255, 0.16)',
            'rgba(10, 132, 255, 0.2)'
          ]
        }
      },
      splitLine: {
        lineStyle: {
          color: gridColor
        }
      },
      axisLine: {
        lineStyle: {
          color: gridColor
        }
      },
      axisName: {
        color: textColor
      }
    },
    series: [{
      name: '能力评估',
      type: 'radar',
      data: [{
        value: props.data.map(item => item.value),
        name: '当前能力',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: primarySoft },
            { offset: 1, color: 'rgba(10, 132, 255, 0.05)' }
          ])
        },
        lineStyle: {
          color: primary,
          width: 2
        },
        itemStyle: {
          color: primary
        },
        symbolSize: 6
      }]
    }]
  }

  chartInstance.setOption(option)
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

// 监听尺寸变化
watch(() => [props.width, props.height], () => {
  if (chartInstance) {
    chartInstance.resize()
  }
})

// 组件挂载时初始化
onMounted(() => {
  initChart()
})

const destroyChart = () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

onBeforeUnmount(destroyChart)

defineExpose({
  resize: () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  },
  destroy: destroyChart
})
</script>

<style scoped>
.radar-chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.radar-chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>
