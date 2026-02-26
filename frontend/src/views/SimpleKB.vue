<template>
  <div class="simple-kb-container">
    <div class="header">
      <h2>📚 知识库管理</h2>
      <p class="subtitle">上传和管理您的知识文档</p>
    </div>

    <!-- 知识库列表 -->
    <div class="kb-list">
      <el-card
        v-for="kb in knowledgeBases"
        :key="kb.id"
        class="kb-card"
        shadow="hover"
      >
        <div class="kb-header">
          <h3>{{ kb.name || kb.title }}</h3>
          <el-button
            type="primary"
            size="small"
            @click="openUploadDialog(kb)"
          >
            上传文档
          </el-button>
        </div>
        <p class="kb-description">{{ kb.description || '暂无描述' }}</p>
        <div class="kb-meta">
          <span>文档数: {{ kb.document_count || 0 }}</span>
        </div>
      </el-card>

      <!-- 创建知识库按钮 -->
      <el-card class="kb-card create-card" @click="showCreateDialog = true">
        <div class="create-content">
          <el-icon :size="40"><Plus /></el-icon>
          <p>创建新知识库</p>
        </div>
      </el-card>
    </div>

    <!-- 创建知识库对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建知识库"
      width="500px"
    >
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="createForm.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createKnowledgeBase" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".pdf,.docx,.txt"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、DOCX、TXT 格式，最大 10MB
              </div>
            </template>
          </el-upload>
          <div v-if="selectedFile" class="file-info">
            已选择: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="uploadDocument" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const knowledgeBases = ref<any[]>([])
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const creating = ref(false)
const uploading = ref(false)
const selectedFile = ref<File | null>(null)
const currentKbId = ref('')
const uploadRef = ref()

const createForm = ref({
  name: '',
  description: ''
})

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const response = await api.get('/knowledge/')
    knowledgeBases.value = response.data.results || response.data || []
  } catch (err: any) {
    ElMessage.error('加载知识库失败: ' + (err.response?.data?.error || err.message))
  }
}

// 创建知识库
const createKnowledgeBase = async () => {
  if (!createForm.value.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }

  creating.value = true
  try {
    await api.post('/knowledge/', {
      name: createForm.value.name,
      description: createForm.value.description,
      category: '通用'
    })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    createForm.value = { name: '', description: '' }
    loadKnowledgeBases()
  } catch (err: any) {
    ElMessage.error('创建失败: ' + (err.response?.data?.error || err.message))
  } finally {
    creating.value = false
  }
}

// 显示上传对话框
const openUploadDialog = (kb: any) => {
  currentKbId.value = kb.id
  selectedFile.value = null
  showUploadDialog.value = true
}

// 处理文件选择
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

// 上传文档
const uploadDocument = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    await api.post(`/knowledge/${currentKbId.value}/documents/`, formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    selectedFile.value = null
    loadKnowledgeBases()
  } catch (err: any) {
    ElMessage.error('上传失败: ' + (err.response?.data?.error || err.message))
  } finally {
    uploading.value = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.simple-kb-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.kb-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.kb-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.kb-card:hover {
  transform: translateY(-5px);
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.kb-header h3 {
  margin: 0;
  color: #303133;
}

.kb-description {
  color: #909399;
  font-size: 14px;
  margin: 10px 0;
}

.kb-meta {
  color: #606266;
  font-size: 12px;
}

.create-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 150px;
  border: 2px dashed #dcdfe6;
}

.create-content {
  text-align: center;
  color: #909399;
}

.create-content p {
  margin-top: 10px;
  font-size: 14px;
}

.file-info {
  margin-top: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
}
</style>

