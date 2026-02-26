<template>
  <div class="answer-shell">
    <div class="answer-hero">
      <div class="hero-left">
        <span class="hero-badge">
          <AppleIcon name="sparkles" :size="14" />
          AI 智能分析
        </span>
        <h3 v-html="summaryHtml"></h3>
        <p class="hero-subtitle">系统基于知识库即时生成，重点结论如下：</p>
      </div>
      <div class="hero-meta">
        <div class="meta-chip">
          <AppleIcon name="clock" :size="14" />
          {{ formattedTimestamp }}
        </div>
        <div class="meta-chip">
          <AppleIcon name="document" :size="14" />
          {{ parsedAnswer.sources.length }} 条引用
        </div>
        <div class="meta-chip" :class="`confidence-${confidenceTone}`">
          <AppleIcon name="graph" :size="14" />
          置信度 {{ confidencePercent }}%
        </div>
      </div>
      <div class="confidence-bar">
        <div class="confidence-bar__fill" :style="{ width: confidencePercent + '%' }"></div>
      </div>
    </div>

    <div class="sections-grid">
      <div
        v-for="(section, index) in parsedAnswer.sections"
        :key="index"
        class="section-card"
        :class="`section-card--${getSectionAccent(section)}`"
      >
        <div class="section-card__header">
          <div class="section-icon">
            <AppleIcon :name="getSectionIcon(section)" :size="18" />
          </div>
          <div class="section-title">
            {{ prettifyTitle(section.title) }}
          </div>
        </div>
        <div class="section-card__body" v-html="formatContent(section.content, section.type)"></div>
      </div>
    </div>

    <div class="sources-panel" v-if="parsedAnswer.sources.length">
      <div class="panel-header">
        <div>
          <div class="panel-title">参考文档</div>
          <p class="panel-desc">以下文档为回答提供依据，相关性越高颜色越深。</p>
        </div>
        <el-tag size="large" type="info">
          <AppleIcon name="archivebox" :size="14" />
          共 {{ parsedAnswer.sources.length }} 条
        </el-tag>
      </div>
      <div class="sources-grid">
        <div
          v-for="source in parsedAnswer.sources"
          :key="source.title"
          class="source-card"
          @click="viewSource(source)"
        >
          <div class="source-chip">
            <AppleIcon name="bookmark" :size="12" />
            {{ Math.round(source.relevance * 100) }}% 相关
          </div>
          <div class="source-name">{{ source.title }}</div>
          <div class="source-preview">{{ source.preview }}</div>
        </div>
      </div>
    </div>

    <div class="answer-actions">
      <el-button @click="copyAnswer">
        <AppleIcon name="doc.on.doc" :size="16" />
        复制回答
      </el-button>
      <el-button @click="exportAnswer">
        <AppleIcon name="square.and.arrow.down" :size="16" />
        导出
      </el-button>
      <el-button @click="shareAnswer">
        <AppleIcon name="square.and.arrow.up" :size="16" />
        分享
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import { parseAnswer, formatContent, type AnswerSection } from '@/utils/answerParser'

interface Props {
  content: string
  sources?: any[]
  timestamp?: Date
}

const props = withDefaults(defineProps<Props>(), {
  sources: () => [],
  timestamp: () => new Date()
})

const parsedAnswer = computed(() => parseAnswer(props.content))
const confidencePercent = computed(() => Math.round(parsedAnswer.value.confidence * 100))
const confidenceTone = computed(() => {
  if (confidencePercent.value >= 80) return 'high'
  if (confidencePercent.value >= 60) return 'medium'
  return 'low'
})
const formattedTimestamp = computed(() =>
  new Date(props.timestamp).toLocaleString('zh-CN', {
    hour12: false,
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
)
const formattedSummary = computed(() => {
  if (parsedAnswer.value.summary) {
    return parsedAnswer.value.summary
  }
  return parsedAnswer.value.rawContent.split('\n').find(Boolean) || 'AI 已完成分析，请查看下方详情。'
})

const summaryHtml = computed(() => formatContent(formattedSummary.value, 'text'))

const copyAnswer = async () => {
  try {
    await navigator.clipboard.writeText(props.content)
    ElMessage.success('回答已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const exportAnswer = () => {
  const blob = new Blob([props.content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `AI回答_${new Date().toISOString().slice(0, 10)}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success('回答已导出')
}

const shareAnswer = () => {
  if (navigator.share) {
    navigator.share({
      title: 'AI回答',
      text: parsedAnswer.value.summary,
      url: window.location.href
    })
  } else {
    copyAnswer()
    ElMessage.success('回答链接已复制到剪贴板')
  }
}

const viewSource = (source: any) => {
  ElMessage.info(`查看来源: ${source.title}`)
}

const iconMap: Record<string, string> = {
  text: 'doc.text',
  list: 'list.bullet',
  code: 'chevron.left.slash.chevron.right',
  table: 'tablecells',
  quote: 'text.quote'
}

const getSectionIcon = (section: AnswerSection) => {
  if (/原因|诊断|分析|评估/.test(section.title)) return 'exclamationmark.circle'
  if (/建议|措施|处理|方案/.test(section.title)) return 'checkmark.seal'
  if (/注意|风险|提示/.test(section.title)) return 'warning'
  return iconMap[section.type] || 'doc.text'
}

const getSectionAccent = (section: AnswerSection) => {
  if (/建议|措施|处理|方案/.test(section.title)) return 'action'
  if (/原因|诊断|分析|评估/.test(section.title)) return 'insight'
  if (/数据|指标|监测/.test(section.title)) return 'metric'
  return 'neutral'
}

const prettifyTitle = (title: string) => {
  if (!title || title === '回答内容') return '分析内容'
  return title.replace(/^[#\d\.\s]+/, '')
}
</script>

<style scoped>
.answer-shell {
  max-width: 880px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.answer-hero {
  background: linear-gradient(135deg, #f6f9ff 0%, #eef3ff 45%, #ffffff 100%);
  border-radius: 28px;
  padding: 28px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
}

.hero-left h3 {
  margin: 12px 0 10px;
  font-size: 20px;
  color: #111827;
  line-height: 1.5;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(10, 132, 255, 0.15);
  color: #0a84ff;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.hero-subtitle {
  margin: 0;
  color: #4b5563;
}

.hero-meta {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  font-size: 13px;
  color: #374151;
  background: #fff;
}

.confidence-bar {
  margin-top: 18px;
  height: 6px;
  background: rgba(15, 23, 42, 0.08);
  border-radius: 999px;
  overflow: hidden;
}

.confidence-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, #34d399, #10b981);
  border-radius: 999px;
  transition: width 0.4s ease;
}

.confidence-high {
  border-color: #10b981;
  color: #065f46;
}

.confidence-medium {
  border-color: #f59e0b;
  color: #92400e;
}

.confidence-low {
  border-color: #f87171;
  color: #991b1b;
}

.sections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}

.section-card {
  border-radius: 22px;
  padding: 20px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #fff;
  box-shadow: 0 18px 35px rgba(15, 23, 42, 0.08);
  min-height: 200px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-card--insight {
  background: linear-gradient(135deg, #eef2ff, #ffffff);
  border-color: rgba(79, 70, 229, 0.25);
}

.section-card--action {
  background: linear-gradient(135deg, #ecfccb, #ffffff);
  border-color: rgba(101, 163, 13, 0.35);
}

.section-card--metric {
  background: linear-gradient(135deg, #cffafe, #ffffff);
  border-color: rgba(6, 182, 212, 0.35);
}

.section-card__header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.05);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.section-title {
  font-weight: 600;
  color: #111827;
}

.section-card__body {
  color: #374151;
  line-height: 1.7;
  font-size: 14px;
}

.section-card__body :deep(p) {
  margin: 0 0 8px;
}

.section-card__body :deep(br) {
  content: '';
  display: block;
  margin-bottom: 8px;
}

.sources-panel {
  background: #fff;
  border-radius: 28px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  padding: 24px;
  box-shadow: 0 25px 50px rgba(15, 23, 42, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.panel-desc {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 14px;
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.source-card {
  border-radius: 18px;
  padding: 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #f8fafc;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.source-card:hover {
  transform: translateY(-3px);
  border-color: #0ea5e9;
}

.source-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(14, 165, 233, 0.1);
  color: #0369a1;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  margin-bottom: 8px;
}

.source-name {
  font-weight: 600;
  color: #111827;
  margin-bottom: 6px;
}

.source-preview {
  color: #475467;
  font-size: 13px;
  line-height: 1.5;
}

.answer-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.answer-actions .el-button {
  border-radius: 999px;
  padding: 10px 18px;
}

@media (max-width: 768px) {
  .answer-shell {
    padding: 0 12px;
  }
  .answer-hero {
    padding: 20px;
  }
  .sections-grid {
    grid-template-columns: 1fr;
  }
  .answer-actions {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
