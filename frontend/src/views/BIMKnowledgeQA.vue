<template>
  <div class="bim-qa-container">
    <header class="page-header">
      <h1>BIM 知识库 · AI 问答</h1>
      <p>BIM 数据 → JSON 入库 → 智能问答</p>
    </header>

    <el-tabs v-model="activeTab">
      <!-- 知识库与 BIM 上传 -->
      <el-tab-pane label="知识库 / BIM 上传" name="kb">
        <div class="kb-section">
          <el-button type="primary" @click="showCreateKb = true">创建知识库</el-button>
          <el-select
            v-model="currentKbId"
            placeholder="选择知识库"
            filterable
            style="width: 320px; margin-left: 12px;"
            @change="loadDocuments"
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.title"
              :value="kb.id"
            />
          </el-select>
        </div>
        <div v-if="currentKbId" class="upload-section">
          <h3>上传 BIM 数据（.json / .ifc）</h3>
          <el-upload
            :auto-upload="true"
            :http-request="doBimUpload"
            :before-upload="beforeBimUpload"
            :limit="1"
            accept=".json,.ifc"
            :file-list="bimFileList"
          >
            <el-button type="primary">选择 .json 或 .ifc 文件</el-button>
            <template #tip>
              <div class="tip">自动转为 JSON 入库并向量化，支持 BIM 导出 JSON 或 IFC 文件（IFC 需服务端安装 ifcopenshell）</div>
            </template>
          </el-upload>
          <div class="doc-list">
            <h4>已入库文档</h4>
            <ul v-if="documents.length">
              <li v-for="d in documents" :key="d.id">{{ d.title }}</li>
            </ul>
            <p v-else class="empty">暂无文档</p>
          </div>
        </div>
        <el-dialog v-model="showCreateKb" title="创建知识库" width="400px">
          <el-form :model="createForm" label-width="80px">
            <el-form-item label="名称">
              <el-input v-model="createForm.title" placeholder="知识库名称" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="createForm.description" type="textarea" :rows="2" placeholder="选填" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showCreateKb = false">取消</el-button>
            <el-button type="primary" @click="createKnowledgeBase">创建</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <!-- AI 问答 -->
      <el-tab-pane label="AI 问答" name="qa">
        <div class="qa-section">
          <el-select
            v-model="qaKbId"
            placeholder="选择知识库"
            filterable
            style="width: 100%; margin-bottom: 12px;"
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.title"
              :value="kb.id"
            />
          </el-select>
          <el-input
            v-model="question"
            type="textarea"
            :rows="3"
            placeholder="输入问题，例如：BIM 里塔吊安全距离是多少？"
          />
          <el-button type="primary" :loading="qaLoading" @click="ask" style="margin-top: 12px;">提问</el-button>
          <div v-if="answer" class="answer-box">
            <h4>回答</h4>
            <div class="answer-content">{{ answer }}</div>
            <div v-if="sources.length" class="sources">
              <strong>参考来源：</strong>
              <span>{{ sources.join('、') }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const activeTab = ref('kb')
const knowledgeBases = ref<any[]>([])
const currentKbId = ref('')
const qaKbId = ref('')
const documents = ref<any[]>([])
const showCreateKb = ref(false)
const createForm = ref({ title: '', description: '' })
const question = ref('')
const qaLoading = ref(false)
const answer = ref('')
const sources = ref<string[]>([])

const bimFileList = ref<any[]>([])

function beforeBimUpload(file: File) {
  const ok = file.name.toLowerCase().endsWith('.json') || file.name.toLowerCase().endsWith('.ifc')
  if (!ok) {
    ElMessage.error('仅支持 .json 或 .ifc 文件')
    return false
  }
  return true
}

async function doBimUpload(options: { file: File }) {
  if (!currentKbId.value) {
    ElMessage.warning('请先选择知识库')
    return
  }
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    await api.post(`/knowledge/${currentKbId.value}/bim/`, formData)
    ElMessage.success('BIM 数据已入库')
    bimFileList.value = []
    loadDocuments()
  } catch (e: any) {
    const msg = e?.response?.data?.error || '上传失败'
    ElMessage.error(msg)
  }
}

async function loadKnowledgeBases() {
  try {
    const res = await api.get('/knowledge/')
    knowledgeBases.value = res.data?.results ?? res.data ?? []
    if (knowledgeBases.value.length && !currentKbId.value) {
      currentKbId.value = knowledgeBases.value[0].id
      qaKbId.value = knowledgeBases.value[0].id
    }
    if (currentKbId.value) loadDocuments()
  } catch (e) {
    ElMessage.error('加载知识库失败')
  }
}

async function loadDocuments() {
  if (!currentKbId.value) return
  try {
    const res = await api.get(`/knowledge/${currentKbId.value}/documents/`)
    documents.value = res.data ?? []
  } catch {
    documents.value = []
  }
}

async function createKnowledgeBase() {
  if (!createForm.value.title?.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  try {
    await api.post('/knowledge/', {
      title: createForm.value.title,
      description: createForm.value.description || '',
      category: 'general',
    })
    ElMessage.success('创建成功')
    showCreateKb.value = false
    createForm.value = { title: '', description: '' }
    loadKnowledgeBases()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.response?.data?.error || '创建失败')
  }
}

async function ask() {
  if (!question.value?.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  if (!qaKbId.value) {
    ElMessage.warning('请先选择知识库')
    return
  }
  qaLoading.value = true
  answer.value = ''
  sources.value = []
  try {
    const res = await api.post('/chat/simple-query/', {
      question: question.value,
      knowledge_base_id: qaKbId.value,
    })
    answer.value = res.data?.answer ?? ''
    sources.value = res.data?.sources ?? []
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error || '问答失败')
  } finally {
    qaLoading.value = false
  }
}

onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.bim-qa-container {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px;
}
.page-header {
  text-align: center;
  margin-bottom: 24px;
}
.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
}
.page-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
.kb-section {
  margin-bottom: 20px;
}
.upload-section {
  margin-top: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.upload-section h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
}
.tip {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
}
.doc-list {
  margin-top: 16px;
}
.doc-list h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
}
.doc-list ul {
  margin: 0;
  padding-left: 20px;
}
.doc-list .empty {
  margin: 0;
  color: #999;
  font-size: 13px;
}
.qa-section .answer-box {
  margin-top: 20px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
}
.qa-section .answer-box h4 {
  margin: 0 0 8px 0;
}
.qa-section .answer-content {
  white-space: pre-wrap;
  line-height: 1.6;
}
.qa-section .sources {
  margin-top: 12px;
  font-size: 12px;
  color: #666;
}
</style>
