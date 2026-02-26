<template>
  <div class="medical-shell">
    <section class="medical-hero">
      <video class="hero-video" autoplay muted loop playsinline>
        <source :src="medicalVideoSrc" type="video/mp4" />
      </video>
      <div class="hero-overlay"></div>
      <div class="hero-header">
        <div>
          <p class="eyebrow">医疗 · 智能助手</p>
          <h2>症状诊断与药品知识一体化</h2>
          <p class="subtitle">支持多症状输入、自动匹配可能疾病，并对药品禁忌做出提醒。</p>
        </div>
        <el-button text class="text-link" @click="goHome">
          <AppleIcon name="arrow-left" :size="16" />
          返回首页
        </el-button>
      </div>
    </section>

    <div class="content-grid">
      <section class="column-card column-card--diagnosis">
        <div class="column-header">
          <div>
            <p class="eyebrow">症状匹配</p>
            <h3>智能诊断建议</h3>
          </div>
          <el-tag type="success" size="small">Beta</el-tag>
        </div>

        <el-form :model="diagnosisForm" label-position="top" class="diagnosis-form">
          <el-form-item label="症状清单">
            <el-select
              v-model="diagnosisForm.symptoms"
              multiple
              filterable
              placeholder="请选择或搜索症状"
              style="width: 100%"
            >
              <el-option
                v-for="symptom in symptomOptions"
                :key="symptom.id"
                :label="symptom.name"
                :value="symptom.name"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="症状描述（可选）">
            <el-input
              v-model="diagnosisForm.notes"
              type="textarea"
              :rows="3"
              placeholder="补充症状持续时间、伴随症状等信息"
            />
          </el-form-item>

          <div class="pill-row">
            <span
              class="pill"
              :class="{ active: diagnosisForm.symptoms.includes(symptom) }"
              v-for="symptom in quickSymptoms"
              :key="symptom"
              @click="toggleSymptom(symptom)"
            >
              {{ symptom }}
            </span>
          </div>

          <div class="form-actions">
            <el-button text @click="resetDiagnosis">清空</el-button>
            <el-button type="primary" :loading="diagnosing" @click="submitDiagnosis">
              生成诊断建议
            </el-button>
          </div>
        </el-form>

        <div class="diagnosis-result" v-if="diagnosisResult">
          <div class="result-header">
            <div>
              <p class="eyebrow">可能疾病</p>
              <h3>{{ diagnosisResult.probable_disease || '待匹配' }}</h3>
            </div>
            <el-tag :type="riskTagType">{{ diagnosisRiskLabel }}</el-tag>
          </div>
          <p class="result-text">{{ diagnosisResult.recommendations }}</p>
        </div>
        <div v-else class="result-placeholder">
          请选择症状并提交，即可获得人工智能建议。
        </div>
      </section>

      <section class="column-card column-card--drug">
        <div class="column-header">
          <div>
            <p class="eyebrow">药品知识</p>
            <h3>常用药物与禁忌</h3>
          </div>
          <el-tag type="info" size="small">{{ drugs.length }} 种</el-tag>
        </div>

        <el-skeleton v-if="loadingDrugs" :rows="4" animated />
        <div v-else class="drug-list">
          <el-empty v-if="!drugs.length" description="暂无药品数据" />
          <div v-else>
            <div v-for="drug in drugs" :key="drug.id" class="drug-row">
              <div class="drug-head">
                <h4>{{ drug.name }}</h4>
                <span class="drug-version">{{ drug.dosage || '遵医嘱' }}</span>
              </div>
              <p>{{ drug.indication || '暂无适应症信息' }}</p>
              <small>禁忌：{{ drug.contraindications || '无' }}</small>
            </div>
          </div>
        </div>

        <el-button type="primary" plain class="full-width">生成治疗建议</el-button>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import AppleIcon from '@/components/AppleIcon.vue'
import medicalVideo from '@/video/医疗.mp4?url'

const router = useRouter()

// 视频资源
const medicalVideoSrc = medicalVideo

const symptomOptions = ref<any[]>([])
const drugs = ref<any[]>([])
const loadingDrugs = ref(false)
const diagnosisForm = reactive({
  symptoms: [] as string[],
  notes: ''
})
const diagnosing = ref(false)
const diagnosisResult = ref<any | null>(null)
const quickSymptoms = ['发热', '咳嗽', '胸闷', '乏力']

const diagnosisIcon = computed(() => {
  if (!diagnosisResult.value) return 'info'
  if (diagnosisResult.value.risk_level === 'high') return 'error'
  if (diagnosisResult.value.risk_level === 'medium') return 'warning'
  return 'success'
})

const diagnosisRiskLabel = computed(() => {
  if (!diagnosisResult.value) return '待检测'
  const map: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return map[diagnosisResult.value.risk_level] || '未知'
})

const riskTagType = computed(() => {
  if (!diagnosisResult.value) return 'info'
  return diagnosisResult.value.risk_level === 'high'
    ? 'danger'
    : diagnosisResult.value.risk_level === 'medium'
      ? 'warning'
      : 'success'
})

const fetchSymptoms = async () => {
  try {
    const response = await api.get('/medical/symptoms/')
    symptomOptions.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('加载症状库失败')
  }
}

const fetchDrugs = async () => {
  loadingDrugs.value = true
  try {
    const response = await api.get('/medical/drugs/?page_size=5')
    drugs.value = (response.data.results || response.data).slice(0, 5)
  } catch (error) {
    ElMessage.error('加载药品信息失败')
  } finally {
    loadingDrugs.value = false
  }
}

const submitDiagnosis = async () => {
  if (!diagnosisForm.symptoms.length) {
    ElMessage.warning('请选择至少一个症状')
    return
  }
  diagnosing.value = true
  try {
    const response = await api.post('/medical/diagnoses/', {
      symptoms_input: diagnosisForm.symptoms
    })
    diagnosisResult.value = response.data
    ElMessage.success('诊断建议已生成')
  } catch (error) {
    ElMessage.error('诊断失败，请稍后再试')
  } finally {
    diagnosing.value = false
  }
}

const resetDiagnosis = () => {
  diagnosisForm.symptoms = []
  diagnosisForm.notes = ''
  diagnosisResult.value = null
}

const toggleSymptom = (symptom: string) => {
  const exists = diagnosisForm.symptoms.includes(symptom)
  if (exists) {
    diagnosisForm.symptoms = diagnosisForm.symptoms.filter((item) => item !== symptom)
  } else {
    diagnosisForm.symptoms.push(symptom)
  }
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchSymptoms()
  fetchDrugs()
})
</script>

<style scoped>
.medical-shell {
  padding: 32px 48px;
  background: var(--apple-body-bg);
  min-height: 100vh;
}

.medical-hero {
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

.column-card--diagnosis::before,
.column-card--drug::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 24px 24px 0 0;
}

.column-card--diagnosis::before {
  background: linear-gradient(90deg, #34c759, #a0f0c4);
}

.column-card--drug::before {
  background: linear-gradient(90deg, #0071e3, #a5b4fc);
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.diagnosis-form {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 16px;
  background: rgba(31, 31, 35, 0.04);
}

.pill-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.pill {
  padding: 6px 12px;
  border-radius: var(--apple-pill-radius);
  border: 1px solid var(--apple-border);
  font-size: 12px;
  cursor: pointer;
  color: var(--apple-text-secondary);
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.pill.active {
  border-color: var(--apple-success);
  background: rgba(50, 215, 75, 0.12);
  color: var(--apple-text-primary);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.diagnosis-result,
.result-placeholder {
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  padding: 16px;
  margin-top: auto;
  background: var(--apple-surface);
}

.result-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.result-text {
  color: var(--apple-text-secondary);
}

.drug-list {
  flex: 1;
  overflow: auto;
  margin-bottom: 16px;
}

.drug-row {
  border-bottom: 1px solid var(--apple-border);
  padding: 16px 0;
}

.drug-row:last-child {
  border-bottom: none;
}

.drug-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drug-version {
  font-size: 12px;
  color: var(--apple-text-secondary);
}

.drug-row p {
  color: var(--apple-text-secondary);
  margin-bottom: 4px;
}

.drug-row small {
  color: var(--apple-text-secondary);
}

.full-width {
  width: 100%;
}

@media (max-width: 768px) {
  .medical-shell {
    padding: 24px;
  }
}
</style>

