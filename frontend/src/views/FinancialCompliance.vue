<template>
  <div class="financial-shell">
    <section class="financial-hero">
      <video class="hero-video" autoplay muted loop playsinline>
        <source :src="financialVideoSrc" type="video/mp4" />
      </video>
      <div class="hero-overlay"></div>
      <div class="hero-header">
        <div>
          <p class="eyebrow">金融 · 合规</p>
          <h2>政策时间轴与即时风险检查</h2>
          <p class="subtitle">
            跟踪监管动态、管理版本差异，并对业务流程进行快速风险评估。
          </p>
        </div>
        <el-button text class="text-link" @click="goHome">
          <AppleIcon name="arrow-left" :size="16" />
          返回首页
        </el-button>
      </div>
    </section>

    <div class="content-grid">
      <section class="column-card column-card--timeline">
        <div class="column-header">
          <div>
            <p class="eyebrow">政策库</p>
            <h3>时间轴与版本追踪</h3>
          </div>
          <el-tag type="info" size="small">{{ visiblePolicies.length }} 条</el-tag>
        </div>

        <div class="filter-bar">
          <el-select v-model="categoryFilter" placeholder="全部分类" size="small" class="filter-item">
            <el-option label="全部分类" value="all" />
            <el-option
              v-for="category in categoryOptions"
              :key="category"
              :label="category || '通用'"
              :value="category || '通用'"
            />
          </el-select>
          <el-select v-model="statusFilter" placeholder="全部状态" size="small" class="filter-item">
            <el-option label="全部状态" value="all" />
            <el-option label="草稿" value="draft" />
            <el-option label="生效" value="active" />
            <el-option label="已废止" value="deprecated" />
          </el-select>
          <el-date-picker
            v-model="dateFilter"
            type="daterange"
            unlink-panels
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            size="small"
            class="filter-item"
          />
        </div>

        <el-skeleton v-if="loadingPolicies" :rows="4" animated />
        <div v-else class="timeline-wrapper">
          <el-empty v-if="!visiblePolicies.length" description="暂无匹配的政策" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="policy in visiblePolicies"
              :key="policy.id"
              :timestamp="policy.effective_date || '待定'"
            >
              <div class="policy-row">
                <div class="policy-badge">
                  <el-tag size="small" type="success">{{ policy.category || '通用' }}</el-tag>
                  <el-tag size="small" :type="statusMap[policy.status]?.tag || 'info'">
                    {{ statusMap[policy.status]?.label || '草稿' }}
                  </el-tag>
                </div>
                <h4>{{ policy.title }}</h4>
                <p>{{ policy.summary || '暂无摘要' }}</p>
                <span class="source">{{ policy.source || '内部发布' }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </section>

      <section class="column-card column-card--risk">
        <div class="column-header">
          <div>
            <p class="eyebrow">风险检查</p>
            <h3>业务描述即时评估</h3>
          </div>
          <el-tag type="warning" size="small">Beta</el-tag>
        </div>

        <el-form :model="complianceForm" label-position="top" class="risk-form">
          <el-form-item label="业务场景">
            <el-select v-model="complianceForm.scenario" placeholder="请选择业务场景" size="small">
              <el-option label="互联网代销" value="channel" />
              <el-option label="客户开户" value="onboarding" />
              <el-option label="理财产品" value="wealth" />
            </el-select>
          </el-form-item>
          <el-form-item label="业务描述">
            <el-input
              v-model="complianceForm.description"
              type="textarea"
              :rows="5"
              placeholder="例如：我们计划在 App 上代销某银行的定期存款产品..."
            />
          </el-form-item>
          <div class="form-actions">
            <el-button @click="resetForm" text>清空</el-button>
            <el-button type="primary" :loading="submitting" @click="submitComplianceCheck">
              立即检查
            </el-button>
          </div>
        </el-form>

        <div class="result-panel" v-if="complianceResult">
          <div class="result-header">
            <span class="risk-label" :class="`risk-${complianceResult.risk_level}`">{{ riskTitle }}</span>
            <span class="result-time">{{ complianceResult.created_at || '刚刚' }}</span>
          </div>
          <p class="result-text">{{ complianceResult.suggestions }}</p>
          <div class="result-tags">
            <el-tag v-for="tag in complianceResult.detected_tags" :key="tag" type="info">
              {{ tag }}
            </el-tag>
          </div>
        </div>
        <div v-else class="result-placeholder">
          <p>提交业务描述即可获得风险等级与建议。</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import AppleIcon from '@/components/AppleIcon.vue'
import financialVideo from '@/video/金融.mp4?url'

const router = useRouter()

// 视频资源
const financialVideoSrc = financialVideo

const policies = ref<any[]>([])
const loadingPolicies = ref(false)
const complianceForm = reactive({
  scenario: '',
  description: ''
})
const submitting = ref(false)
const complianceResult = ref<any | null>(null)
const categoryFilter = ref('all')
const statusFilter = ref('all')
const dateFilter = ref<[Date, Date] | null>(null)

const riskIcon = computed(() => {
  if (!complianceResult.value) return 'info'
  if (complianceResult.value.risk_level === 'high') return 'error'
  if (complianceResult.value.risk_level === 'medium') return 'warning'
  return 'success'
})

const riskTitle = computed(() => {
  if (!complianceResult.value) return ''
  const map: Record<string, string> = {
    low: '低风险建议',
    medium: '中风险提醒',
    high: '高风险警报'
  }
  return map[complianceResult.value.risk_level] || '风险建议'
})

const statusMap: Record<string, { label: string; tag: string }> = {
  draft: { label: '草稿', tag: 'info' },
  active: { label: '生效', tag: 'success' },
  deprecated: { label: '已废止', tag: 'danger' }
}

const categoryOptions = computed(() => {
  const set = new Set<string>()
  policies.value.forEach((p) => set.add(p.category || '通用'))
  return Array.from(set)
})

const visiblePolicies = computed(() => {
  return policies.value.filter((policy) => {
    const normalizedCategory = policy.category || '通用'
    const matchCategory =
      categoryFilter.value === 'all' || normalizedCategory === categoryFilter.value
    const matchStatus = statusFilter.value === 'all' || policy.status === statusFilter.value

    let matchDate = true
    if (dateFilter.value && policy.effective_date) {
      const [start, end] = dateFilter.value
      const effectiveDate = new Date(policy.effective_date)
      matchDate = effectiveDate >= start && effectiveDate <= end
    }

    return matchCategory && matchStatus && matchDate
  })
})

const fetchPolicies = async () => {
  loadingPolicies.value = true
  try {
    const response = await api.get('/financial/policies/')
    policies.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('加载政策数据失败')
  } finally {
    loadingPolicies.value = false
  }
}

const submitComplianceCheck = async () => {
  if (!complianceForm.description.trim()) {
    ElMessage.warning('请先输入业务描述')
    return
  }
  submitting.value = true
  try {
    const response = await api.post('/financial/compliance-checks/', {
      business_description: complianceForm.description,
      scenario: complianceForm.scenario
    })
    complianceResult.value = response.data
    ElMessage.success('合规检查完成')
  } catch (error) {
    ElMessage.error('提交失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  complianceForm.scenario = ''
  complianceForm.description = ''
  complianceResult.value = null
  dateFilter.value = null
  statusFilter.value = 'all'
  categoryFilter.value = 'all'
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchPolicies()
})
</script>

<style scoped>
.financial-shell {
  padding: 32px 48px;
  background: var(--apple-body-bg);
  min-height: 100vh;
}

.financial-hero {
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

.hero-header h2 {
  font-size: 32px;
  font-weight: 700;
  margin: 8px 0 12px;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.hero-header .subtitle {
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.hero-header .eyebrow {
  color: rgba(255, 255, 255, 0.85);
}

.column-card {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-card-radius);
  padding: 28px 32px;
  margin-bottom: 24px;
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

.column-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
}

.column-card--timeline::before,
.column-card--risk::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 24px 24px 0 0;
}

.column-card--timeline::before {
  background: linear-gradient(90deg, #0071e3, #a5b4fc);
}

.column-card--risk::before {
  background: linear-gradient(90deg, #34c759, #a0f0c4);
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.filter-bar :deep(.el-input__wrapper),
.filter-bar :deep(.el-date-editor.el-input__wrapper) {
  border: 1px solid var(--apple-border);
  box-shadow: none !important;
  border-radius: var(--apple-control-radius);
}

.timeline-wrapper {
  flex: 1;
  overflow: auto;
  padding-right: 8px;
}

.policy-row {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
}

.policy-row h4 {
  margin: 8px 0;
}

.policy-row p {
  color: var(--apple-text-secondary);
  margin-bottom: 8px;
}

.policy-badge {
  display: flex;
  gap: 8px;
}

.source {
  font-size: 12px;
  color: var(--apple-text-secondary);
}

.risk-form {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 16px;
  background: rgba(31, 31, 35, 0.04);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.result-panel {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
  position: relative;
  background: var(--apple-surface);
}

.result-panel::before {
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
  margin-bottom: 8px;
}

.risk-label {
  font-weight: 600;
}

.risk-low {
  color: #0f9d58;
}

.risk-medium {
  color: #f9a825;
}

.risk-high {
  color: #d93025;
}

.result-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.result-placeholder {
  border: 1px dashed var(--apple-border);
  border-radius: 20px;
  padding: 24px;
  color: var(--apple-text-secondary);
  text-align: center;
}

@media (max-width: 768px) {
  .financial-shell {
    padding: 24px;
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-item,
  .risk-form {
    width: 100%;
  }
}
</style>

