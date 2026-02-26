<template>
  <div class="app-simple">
    <header class="header">
      <div class="header-left">
        <div class="logo-pill">
          <AppleIcon name="cube" :size="22" />
        </div>
        <div class="title-block">
          <h1>BIM · 智慧工地知识库</h1>
          <p>一站式管理 BIM 数据与 AI 问答</p>
        </div>
      </div>
      <div class="header-actions">
        <span class="user-name">
          <AppleIcon name="user" :size="16" />
          <span class="user-name-text">{{ authStore.user?.username }}</span>
        </span>
        <el-button size="small" @click="goKnowledge">
          <AppleIcon name="folder" :size="14" />
          知识库管理
        </el-button>
        <el-button link type="primary" @click="handleLogout">退出登录</el-button>
      </div>
    </header>

    <main class="main">
      <section class="section section-kb">
        <div class="section-header">
          <div class="section-title">
            <div class="section-icon kb">
              <AppleIcon name="building.2" :size="18" />
            </div>
            <div>
              <h2>BIM 知识库与模型</h2>
              <p>按项目集中管理 BIM JSON / IFC 及文档</p>
            </div>
          </div>
        </div>
        <div class="kb-bar">
          <el-input
            v-model="createName"
            placeholder="输入新案场或知识库名称，例如“1#塔楼结构 BIM”"
            class="kb-name-input"
          />
          <el-button type="primary" @click="createKb">
            <AppleIcon name="plus" :size="14" />
            创建知识库
          </el-button>
        </div>
        <el-select
          v-model="currentKbId"
          placeholder="选择要操作的 BIM 知识库"
          class="kb-select"
          @change="loadDocs"
        >
          <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.title" :value="kb.id" />
        </el-select>
        <div v-if="currentKbId" class="upload-bar">
          <el-upload
            :show-file-list="false"
            :before-upload="beforeBim"
            :http-request="doUpload"
            accept=".json,.ifc"
          >
            <el-button type="primary" size="small">
              <AppleIcon name="upload" :size="14" />
              上传 BIM (.json / .ifc)
            </el-button>
          </el-upload>
          <p class="upload-tip">
            支持 BIM 导出的 JSON 或 IFC 文件，后端自动解析为结构化元素并向量化入库。
          </p>
        </div>
        <p v-if="currentKbId" class="doc-tip">
          <AppleIcon name="document" :size="14" />
          当前知识库已入库 {{ documents.length }} 个文档
        </p>
      </section>

      <section class="section section-qa">
        <div class="section-header">
          <div class="section-title">
            <div class="section-icon qa">
              <AppleIcon name="sparkles" :size="18" />
            </div>
            <div>
              <h2>现场问题 · AI 专业解答</h2>
              <p>基于 BIM 知识库 + 标准答案的智慧工地问答</p>
            </div>
          </div>
        </div>
        <el-select
          v-model="qaKbId"
          placeholder="选择用于回答的 BIM 知识库"
          class="kb-select"
        >
          <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.title" :value="kb.id" />
        </el-select>
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          class="question-input"
          placeholder="例如：塔吊 TC-01 在当前 BIM 模型中规划的最小安全回转半径是多少？"
        />
        <div class="qa-actions">
          <span class="qa-hint">
            <AppleIcon name="info" :size="14" />
            先检索知识库，无强相关结果时由 AI 按自身知识回答。
          </span>
          <el-button type="primary" :loading="qaLoading" @click="ask">
            <AppleIcon name="arrow-right" :size="14" />
            提交问题
          </el-button>
        </div>
        <div v-if="answer" class="answer-box">
          <div class="answer-text markdown-body" v-html="renderedAnswer"></div>
          <div v-if="answerSource" class="answer-source-tag" :class="answerSource">
            {{ answerSource === 'rag' ? '来自知识库' : '来自AI知识' }}
          </div>
          <div v-if="sources.length" class="sources">
            <AppleIcon name="bookmark" :size="12" />
            参考文档：{{ sources.join('、') }}
          </div>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import AppleIcon from '@/components/AppleIcon.vue'

marked.setOptions({ gfm: true, breaks: true })

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function goKnowledge() {
  router.push('/knowledge')
}

const createName = ref('')
const knowledgeBases = ref<any[]>([])
const currentKbId = ref('')
const documents = ref<any[]>([])
const qaKbId = ref('')
const question = ref('')
const qaLoading = ref(false)
const answer = ref('')
const sources = ref<string[]>([])
const answerSource = ref<'rag' | 'general' | ''>('')
const error = ref('')

const renderedAnswer = computed(() => {
  const raw = answer.value
  if (!raw || typeof raw !== 'string') return ''
  return marked.parse(raw) as string
})

async function loadKb() {
  try {
    const res = await api.get('/knowledge/')
    knowledgeBases.value = Array.isArray(res.data) ? res.data : []
    if (knowledgeBases.value.length && !currentKbId.value) {
      currentKbId.value = knowledgeBases.value[0].id
      qaKbId.value = knowledgeBases.value[0].id
    }
    if (currentKbId.value) loadDocs()
  } catch (e) {
    ElMessage.error('加载知识库失败')
  }
}

async function loadDocs() {
  if (!currentKbId.value) return
  try {
    const res = await api.get(`/knowledge/${currentKbId.value}/documents/`)
    documents.value = Array.isArray(res.data) ? res.data : []
  } catch {
    documents.value = []
  }
}

async function createKb() {
  if (!createName.value.trim()) {
    ElMessage.warning('请输入名称')
    return
  }
  try {
    await api.post('/knowledge/', { title: createName.value.trim(), description: '', category: 'general' })
    ElMessage.success('创建成功')
    createName.value = ''
    loadKb()
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

function beforeBim(file: File) {
  const ok = file.name.toLowerCase().endsWith('.json') || file.name.toLowerCase().endsWith('.ifc')
  if (!ok) {
    ElMessage.error('仅支持 .json 或 .ifc')
    return false
  }
  return true
}

async function doUpload(op: { file: File }) {
  if (!currentKbId.value) {
    ElMessage.warning('请先选择知识库')
    return
  }
  const form = new FormData()
  form.append('file', op.file)
  try {
    await api.post(`/knowledge/${currentKbId.value}/bim/`, form)
    ElMessage.success('已入库')
    loadDocs()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error || '上传失败')
  }
}

async function ask() {
  if (!question.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  error.value = ''
  answer.value = ''
  sources.value = []
  answerSource.value = ''
  qaLoading.value = true
  try {
    const res = await api.post('/chat/ask/', {
      question: question.value,
      knowledge_base_id: qaKbId.value || undefined,
    })
    answer.value = res.data?.answer ?? ''
    sources.value = res.data?.sources ?? []
    answerSource.value = res.data?.answer_source ?? ''
  } catch (e: any) {
    error.value = e?.response?.data?.error || '问答失败'
  } finally {
    qaLoading.value = false
  }
}

onMounted(() => loadKb())
</script>

<style scoped>
.app-simple {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px 40px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
  background: radial-gradient(circle at top left, #e0f2fe 0, transparent 55%),
    radial-gradient(circle at bottom right, #ecfdf3 0, transparent 55%);
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 16px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-pill {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: linear-gradient(135deg, #0ea5e9, #22c55e);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 10px 30px rgba(15, 118, 110, 0.35);
}
.title-block h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}
.title-block p {
  margin: 2px 0 0;
  font-size: 0.9rem;
  color: #64748b;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-name {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.04);
  font-size: 13px;
  color: #475569;
}
.user-name-text {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.main {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.2fr);
  gap: 20px;
  align-items: flex-start;
}
.section {
  padding: 18px 20px 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}
.section-header {
  margin-bottom: 14px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-title h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #0f172a;
}
.section-title p {
  margin: 2px 0 0;
  font-size: 0.85rem;
  color: #64748b;
}
.section-icon {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.section-icon.kb {
  background: rgba(59, 130, 246, 0.12);
  color: #1d4ed8;
}
.section-icon.qa {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}
.kb-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.kb-name-input {
  flex: 1;
}
.kb-select {
  width: 100%;
  margin: 6px 0 4px;
}
.upload-bar {
  margin-top: 10px;
}
.upload-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}
.doc-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 4px;
}
.section-qa {
  border-left: 3px solid rgba(59, 130, 246, 0.4);
}
.question-input {
  margin-top: 6px;
}
.qa-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 8px;
}
.qa-hint {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
}
.answer-box {
  margin-top: 14px;
  padding: 12px 14px;
  background: #f9fafb;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
}
.answer-text {
  line-height: 1.6;
  font-size: 14px;
  color: #111827;
}
.answer-text.markdown-body :deep(h1),
.answer-text.markdown-body :deep(h2),
.answer-text.markdown-body :deep(h3),
.answer-text.markdown-body :deep(h4) {
  margin: 1em 0 0.5em;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}
.answer-text.markdown-body :deep(h1) { font-size: 1.25rem; }
.answer-text.markdown-body :deep(h2) { font-size: 1.1rem; }
.answer-text.markdown-body :deep(h3) { font-size: 1rem; }
.answer-text.markdown-body :deep(h4) { font-size: 0.95rem; }
.answer-text.markdown-body :deep(p) {
  margin: 0.5em 0;
}
.answer-text.markdown-body :deep(ul),
.answer-text.markdown-body :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}
.answer-text.markdown-body :deep(li) {
  margin: 0.25em 0;
}
.answer-text.markdown-body :deep(strong) {
  font-weight: 600;
  color: #0f172a;
}
.answer-text.markdown-body :deep(code) {
  padding: 0.15em 0.4em;
  font-size: 0.9em;
  background: #e5e7eb;
  border-radius: 4px;
}
.answer-text.markdown-body :deep(:first-child) {
  margin-top: 0;
}
.answer-text.markdown-body :deep(:last-child) {
  margin-bottom: 0;
}
.answer-source-tag {
  margin-top: 8px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 6px;
}
.answer-source-tag.rag {
  background: #dbeafe;
  color: #1d4ed8;
}
.answer-source-tag.general {
  background: #fef3c7;
  color: #b45309;
}
.sources {
  margin-top: 8px;
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 4px;
}
.error {
  margin-top: 10px;
  color: #b91c1c;
  font-size: 13px;
}

@media (max-width: 900px) {
  .app-simple {
    padding: 20px 14px 28px;
  }
  .main {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
