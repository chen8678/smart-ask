<template>
  <div class="knowledge-container">
    <!-- 顶部导航 -->
    <el-header class="knowledge-header">
      <div class="header-content">
        <div class="header-left">
          <BrandMark class="header-logo" :size="42" padded circular />
          <el-button @click="goBack" class="back-button">
            <AppleIcon name="arrow-left" :size="16" />
          </el-button>
          <div class="header-title">
            <h2>知识库管理</h2>
            <p>管理和组织您的专业知识库</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="showCreateDialog = true" class="create-button">
            <AppleIcon name="plus" :size="16" />
            创建知识库
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="knowledge-main">
      <div class="knowledge-list">
        <el-card
          v-for="kb in knowledgeBases"
          :key="kb.id"
          class="kb-card"
          @click="viewKnowledgeBase(kb)"
        >
          <div class="kb-header">
            <div class="kb-icon">
              <AppleIcon name="folder" :size="22" />
            </div>
            <div class="kb-info">
              <h3>{{ kb.title }}</h3>
              <p class="kb-description">{{ kb.description || '暂无描述' }}</p>
            </div>
            <el-dropdown @command="(command: string) => handleCommand(command, kb)" @click.stop>
              <el-button type="text" class="more-button">
                <AppleIcon name="more" :size="16" />
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">编辑</el-dropdown-item>
                  <el-dropdown-item command="upload">上传文档</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="kb-meta">
            <div class="kb-tags">
              <el-tag :type="getCategoryType(kb.category)" size="small">{{ getCategoryName(kb.category) }}</el-tag>
            </div>
            <div class="kb-stats">
              <span class="kb-count">
                <AppleIcon name="document" :size="16" />
                {{ kb.document_count }} 个文档
              </span>
              <span class="kb-date">{{ formatDate(kb.created_at) }}</span>
            </div>
          </div>
          
          <!-- 操作按钮组 -->
          <div class="kb-actions">
            <div class="action-row">
              <el-button 
                type="success" 
                size="small" 
                @click.stop="generateLearningContent(kb)"
                :loading="generatingContent === kb.id"
                class="action-btn generate-btn"
              >
                <AppleIcon name="star" :size="14" />
                生成相关内容
              </el-button>
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="viewLearningContent(kb)"
                class="action-btn"
              >
                <AppleIcon name="view" :size="14" />
                查看内容
              </el-button>
            </div>
            <div class="action-row">
              <el-button 
                type="info" 
                size="small" 
                @click.stop="viewDocuments(kb)" 
                class="action-btn"
              >
                <AppleIcon name="document" :size="14" />
                查看文档
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-main>

    <!-- 创建知识库对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建知识库"
      width="500px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入知识库标题" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入知识库描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="createForm.category" placeholder="请选择分类">
            <el-option label="通用" value="general" />
            <el-option label="法律" value="legal" />
            <el-option label="教育" value="education" />
            <el-option label="医疗健康" value="healthcare" />
            <el-option label="金融" value="finance" />
            <el-option label="技术" value="technology" />
            <el-option label="商业" value="business" />
            <el-option label="科学" value="science" />
            <el-option label="人文社科" value="humanities" />
            <el-option label="工程" value="engineering" />
            <el-option label="艺术设计" value="arts" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑知识库对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑知识库"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入知识库标题" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            placeholder="请输入知识库描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category" placeholder="请选择分类">
            <el-option label="通用" value="general" />
            <el-option label="法律" value="legal" />
            <el-option label="教育" value="education" />
            <el-option label="医疗健康" value="healthcare" />
            <el-option label="金融" value="finance" />
            <el-option label="技术" value="technology" />
            <el-option label="商业" value="business" />
            <el-option label="科学" value="science" />
            <el-option label="人文社科" value="humanities" />
            <el-option label="工程" value="engineering" />
            <el-option label="艺术设计" value="arts" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEdit" :loading="editing">
          更新
        </el-button>
      </template>
    </el-dialog>

    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      :title="uploadMode === 'file' ? '上传文档' : '导入 JSON 文档'"
      width="520px"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        label-width="100px"
      >
        <el-form-item label="上传方式">
          <el-radio-group v-model="uploadMode">
            <el-radio-button label="file">单文件</el-radio-button>
            <el-radio-button label="json">JSON 导入</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="uploadMode === 'file'" label="选择文件">
          <div class="file-upload-container">
            <el-upload
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="true"
              :limit="1"
              accept=".pdf,.doc,.docx,.txt,.md"
              drag
            >
              <AppleIcon name="upload" :size="24" />
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF、Word、TXT、Markdown 格式，文件大小不超过 10MB
                </div>
              </template>
            </el-upload>
            
            <!-- 备选方案：简单的文件选择 -->
            <div class="simple-file-input">
              <input
                type="file"
                ref="fileInput"
                @change="handleSimpleFileChange"
                accept=".pdf,.doc,.docx,.txt,.md"
                style="display: none"
              />
              <el-button @click="triggerFileInput" type="primary" plain>
                <AppleIcon name="upload" :size="16" />
                选择文件
              </el-button>
              <span v-if="uploadForm.file" class="selected-file">
                已选择: {{ uploadForm.file.name }}
              </span>
            </div>
          </div>
        </el-form-item>

        <el-form-item v-else label="JSON 文件">
          <el-upload
            :auto-upload="false"
            :on-change="handleJsonFileChange"
            :show-file-list="true"
            :limit="1"
            accept=".json"
            drag
          >
            <AppleIcon name="upload" :size="24" />
            <div class="el-upload__text">
              拖拽 JSON 到此或 <em>点击上传</em>
            </div>
            <div class="el-upload__tip">单个 JSON 文件 ≤ 100MB，结构需包含 documents 数组</div>
          </el-upload>
        </el-form-item>

        <el-form-item v-if="uploadMode === 'json'" label="结构示例">
          <div class="json-tip">
            <pre>{
  "documents": [
    {"title": "示例 1", "content": "内容...", "metadata": {"source": "dataset"}},
    {"content": "只提供 content 也可以"}
  ]
}</pre>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button
          v-if="uploadMode === 'file'"
          type="primary"
          @click="handleUpload"
          :loading="uploading"
        >
          上传
        </el-button>
        <el-button
          v-else
          type="primary"
          @click="handleJsonImport"
          :loading="jsonUploading"
        >
          导入 JSON
        </el-button>
      </template>
    </el-dialog>

    <!-- JSON 导入进度对话框 -->
    <el-dialog
      v-model="showImportProgressDialog"
      title="JSON 导入进度"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="import-progress-content">
        <el-progress
          :percentage="importProgress.percentage"
          :status="importProgress.status === 'FAILED' ? 'exception' : (importProgress.status === 'SUCCEEDED' ? 'success' : undefined)"
          :stroke-width="12"
        />
        <div class="progress-stats">
          <div class="stat-item">
            <span class="stat-label">状态：</span>
            <el-tag :type="getImportStatusType(importProgress.status)">
              {{ getImportStatusText(importProgress.status) }}
            </el-tag>
          </div>
          <div class="stat-item">
            <span class="stat-label">总数：</span>
            <span>{{ importProgress.total }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">已创建：</span>
            <span class="text-success">{{ importProgress.created }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">已向量化：</span>
            <span class="text-primary">{{ importProgress.vectorized }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">已跳过：</span>
            <span class="text-warning">{{ importProgress.skipped }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button
          v-if="!['SUCCEEDED', 'FAILED', 'CANCELED'].includes(importProgress.status)"
          @click="cancelImportJob"
        >
          取消任务
        </el-button>
        <el-button
          type="primary"
          @click="showImportProgressDialog = false"
          :disabled="!['SUCCEEDED', 'FAILED', 'CANCELED'].includes(importProgress.status)"
        >
          关闭
        </el-button>
      </template>
    </el-dialog>

    <!-- 相关内容查看对话框 -->
    <el-dialog
      v-model="showLearningContentDialog"
      :title="selectedKB?.title + ' - 相关内容'"
      width="80%"
      :before-close="handleLearningContentClose"
    >
      <div v-if="learningContents.length === 0" class="empty-content">
        <el-empty description="暂无相关内容">
          <el-button type="primary" @click="generateLearningContent(selectedKB)">
            生成相关内容
          </el-button>
        </el-empty>
      </div>
      
      <div v-else class="learning-content">
        <el-tabs v-model="activeTab" type="card">
          <el-tab-pane 
            v-for="content in learningContents" 
            :key="content.id"
            :label="content.content_type_display"
            :name="content.content_type"
          >
            <div class="content-display">
              
              <!-- 内容总结 -->
              <div v-if="content.content_type === 'summary'" class="summary-content">
                <h4>{{ content.content_data.overview }}</h4>
                <div v-for="section in content.content_data.sections" :key="section.title" class="summary-section">
                  <h5>{{ section.title }}</h5>
                  <p>{{ section.summary }}</p>
                  <div v-if="section.key_points && section.key_points.length > 0" class="key-points">
                    <h6>关键要点：</h6>
                    <ul>
                      <li v-for="point in section.key_points" :key="point">{{ point }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <!-- 大纲 -->
              <div v-else-if="content.content_type === 'outline'" class="outline-content">
                <h4>{{ content.content_data.title }}</h4>
                <p>{{ content.content_data.description }}</p>
                <div v-for="chapter in content.content_data.chapters" :key="chapter.number" class="chapter-item">
                  <div class="chapter-header">
                    <span class="chapter-number">{{ chapter.number }}</span>
                    <h5>{{ chapter.title }}</h5>
                    <span class="chapter-time">{{ chapter.estimated_time }}</span>
                  </div>
                  <p>{{ chapter.description }}</p>
                  <div v-if="chapter.key_topics && chapter.key_topics.length > 0" class="key-topics">
                    <el-tag 
                      v-for="topic in chapter.key_topics" 
                      :key="topic"
                      size="small"
                      type="info"
                    >
                      {{ topic }}
                    </el-tag>
                  </div>
                </div>
              </div>
              
              <!-- 关键概念 -->
              <div v-else-if="content.content_type === 'key_concepts'" class="concepts-content">
                <h4>{{ content.content_data.title }}</h4>
                <div class="concepts-grid">
                  <div v-for="concept in content.content_data.concepts" :key="concept.term" class="concept-card">
                    <h5>{{ concept.term }}</h5>
                    <p>{{ concept.definition }}</p>
                    <div v-if="concept.related_docs && concept.related_docs.length > 0" class="related-docs">
                      <span>相关文档：</span>
                      <el-tag 
                        v-for="doc in concept.related_docs" 
                        :key="doc"
                        size="small"
                        type="success"
                      >
                        {{ doc }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 问答集 -->
              <div v-else-if="content.content_type === 'q_and_a'" class="qa-content">
                <h4>{{ content.content_data.title }}</h4>
                <div v-for="qa in content.content_data.questions" :key="qa.id" class="qa-item">
                  <h5>Q{{ qa.id }}: {{ qa.question }}</h5>
                  <p class="answer">{{ qa.answer }}</p>
                  <div class="qa-source">
                    <el-tag size="small" type="info">来源：{{ qa.source }}</el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 文档查看对话框 -->
    <el-dialog
      v-model="showDocumentsDialog"
      :title="selectedKB?.title + ' - 文档列表'"
      width="80%"
      :before-close="handleDocumentsClose"
    >
      <template #header>
        <div class="dialog-header">
          <span>{{ selectedKB?.title }} - 文档列表</span>
        </div>
      </template>
      
      <div v-if="documents.length === 0" class="empty-documents">
        <el-empty description="该知识库暂无文档">
          <div class="empty-actions">
            <el-button type="primary" @click="uploadDocument(selectedKB)">
              上传文档
            </el-button>
            <el-button type="primary" plain @click="startJsonImport(selectedKB)">
              上传 JSON 文档
            </el-button>
          </div>
        </el-empty>
      </div>
      
      <div v-else class="documents-list">
        <div v-for="doc in documents" :key="doc.id" class="document-item">
          <div class="document-header">
            <h4>{{ doc.title }}</h4>
            <div class="document-actions">
              <el-button size="small" @click="viewDocumentContent(doc)">
                <AppleIcon name="view" :size="14" />
                查看内容
              </el-button>
              <el-button size="small" type="danger" @click="deleteDocument(doc)">
                <AppleIcon name="trash" :size="14" />
                删除
              </el-button>
            </div>
          </div>
          <div class="document-meta">
            <el-tag size="small" type="info">{{ doc.content_type }}</el-tag>
            <span class="document-size">{{ formatFileSize(doc.file_size) }}</span>
            <span class="document-date">{{ formatDate(doc.created_at) }}</span>
          </div>
          <div class="document-preview">
            <p>{{ doc.content?.substring(0, 200) }}...</p>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 文档内容查看对话框 -->
    <el-dialog
      v-model="showDocumentContentDialog"
      :title="selectedDocument?.title"
      width="80%"
      :before-close="() => showDocumentContentDialog = false"
      class="document-content-dialog"
    >
      <div v-if="selectedDocument" class="document-content">
        <div class="document-info">
          <el-tag type="info">{{ selectedDocument.content_type }}</el-tag>
          <span class="document-size">{{ formatFileSize(selectedDocument.file_size) }}</span>
          <span class="document-date">{{ formatDate(selectedDocument.created_at) }}</span>
        </div>
        <div class="document-text">
          <pre>{{ selectedDocument.content }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- AI内容生成对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="大模型驱动的内容生成"
      width="700px"
      :before-close="handleGenerateClose"
      class="generate-dialog"
    >
      <div v-if="selectedKB" class="generate-content">
        <!-- 知识库信息卡片 -->
        <div class="kb-info-card">
          <div class="kb-header">
            <div class="kb-icon">
              <AppleIcon name="document" :size="22" />
            </div>
            <div class="kb-details">
              <h4>{{ selectedKB.title }}</h4>
              <p>{{ selectedKB.description || '专业领域知识库' }}</p>
            </div>
          </div>
          <div class="kb-stats">
            <div class="stat-item">
              <el-tag type="primary">{{ getCategoryName(selectedKB.category) }}</el-tag>
            </div>
            <div class="stat-item">
              <AppleIcon name="document" :size="14" />
              <span>{{ selectedKB.document_count }} 个文档</span>
            </div>
            <div class="stat-item">
              <AppleIcon name="star" :size="14" />
              <span>大模型驱动</span>
            </div>
          </div>
        </div>

        <!-- 功能说明 -->
        <div class="feature-description">
          <h5>🎯 智能内容生成</h5>
          <p>基于您的私有知识库，使用先进的大模型技术自动生成专业的学习内容，提升知识利用效率。</p>
        </div>

        <el-form :model="generateForm" :rules="generateRules" ref="generateFormRef" label-width="120px">
          <el-form-item label="AI模型" prop="ai_model">
            <el-select v-model="generateForm.ai_model" placeholder="选择AI模型" style="width: 100%">
              <el-option 
                v-for="model in availableModels" 
                :key="model.id" 
                :label="model.name" 
                :value="model.id"
                :disabled="!model.available"
              >
                <div class="model-option">
                  <span>{{ model.name }}</span>
                  <el-tag v-if="!model.available" type="warning" size="small">未配置</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="生成内容类型" prop="content_types">
            <div class="content-types-section">
              <p class="section-description">选择要生成的专业内容类型：</p>
              <el-checkbox-group v-model="generateForm.content_types" class="content-types-grid">
                <div class="content-type-item">
                  <el-checkbox label="summary">
                    <div class="type-content">
                      <div class="type-icon">📝</div>
                      <div class="type-info">
                        <div class="type-name">内容总结</div>
                        <div class="type-desc">智能提取核心要点</div>
                      </div>
                    </div>
                  </el-checkbox>
                </div>
                <div class="content-type-item">
                  <el-checkbox label="outline">
                    <div class="type-content">
                      <div class="type-icon">📚</div>
                      <div class="type-info">
                        <div class="type-name">学习大纲</div>
                        <div class="type-desc">结构化知识体系</div>
                      </div>
                    </div>
                  </el-checkbox>
                </div>
                <div class="content-type-item">
                  <el-checkbox label="key_concepts">
                    <div class="type-content">
                      <div class="type-icon">🔑</div>
                      <div class="type-info">
                        <div class="type-name">关键概念</div>
                        <div class="type-desc">重要术语解析</div>
                      </div>
                    </div>
                  </el-checkbox>
                </div>
                <div class="content-type-item">
                  <el-checkbox label="q_and_a">
                    <div class="type-content">
                      <div class="type-icon">❓</div>
                      <div class="type-info">
                        <div class="type-name">问答集</div>
                        <div class="type-desc">常见问题解答</div>
                      </div>
                    </div>
                  </el-checkbox>
                </div>
              </el-checkbox-group>
            </div>
          </el-form-item>

        </el-form>

        <!-- 生成进度 -->
        <div v-if="generating" class="generation-progress">
          <el-progress 
            :percentage="generationProgress" 
            :status="generationStatus"
            :stroke-width="8"
          />
          <p class="progress-text">{{ generationText }}</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="handleGenerateClose">取消</el-button>
          <el-button 
          type="primary" 
          @click="handleGenerate" 
          :loading="generating"
          :disabled="generating"
          class="generate-button"
        >
          <template v-if="!generating">
            <AppleIcon name="star" :size="16" />
            启动大模型生成
          </template>
          <template v-else>
            大模型生成中...
          </template>
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import AppleIcon from '@/components/AppleIcon.vue'
import BrandMark from '@/components/BrandMark.vue'

const router = useRouter()

interface KnowledgeBase {
  id: string
  title: string
  description: string
  category: string
  document_count: number
  created_at: string
  updated_at: string
}

const knowledgeBases = ref<KnowledgeBase[]>([])
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showUploadDialog = ref(false)
const uploadMode = ref<'file' | 'json'>('file')
const jsonUploading = ref(false)
const currentImportJobId = ref<string | null>(null)
const importProgress = ref({
  status: '',
  total: 0,
  created: 0,
  vectorized: 0,
  skipped: 0,
  percentage: 0
})
const showImportProgressDialog = ref(false)
const importProgressInterval = ref<number | null>(null)
const creating = ref(false)
const editing = ref(false)
const uploading = ref(false)

// 学习内容相关
const showLearningContentDialog = ref(false)
const showDocumentsDialog = ref(false)
const documents = ref<any[]>([])
const selectedDocument = ref<any>(null)
const showDocumentContentDialog = ref(false)
const selectedKB = ref<any>(null)
const learningContents = ref<any[]>([])
const activeTab = ref('summary')
const generatingContent = ref<string | null>(null)

// AI内容生成相关
const showGenerateDialog = ref(false)
const availableModels = ref<any[]>([])
const generating = ref(false)
const generationProgress = ref(0)

type AnalysisPayload = {
  relevance: string
  content_type: string
  quality_score: number
  confidence: number
  issues: string[]
  suggestions: string[]
}
const generationStatus = ref<'success' | 'exception' | 'warning' | 'active'>('active')
const generationText = ref('')

const generateForm = reactive({
  ai_model: 'deepseek',
  content_types: ['summary', 'outline', 'key_concepts', 'q_and_a'],
  config: {
    max_tokens: 2000,
    temperature: 0.7
  }
})

const generateRules = {
  ai_model: [
    { required: true, message: '请选择AI模型', trigger: 'change' }
  ],
  content_types: [
    { required: true, message: '请选择至少一种内容类型', trigger: 'change' }
  ]
}

const createForm = reactive({
  title: '',
  description: '',
  category: 'ai'
})

const editForm = reactive({
  id: '',
  title: '',
  description: '',
  category: 'ai'
})

const uploadForm = reactive({
  knowledge_base_id: '',
  file: null as File | null
})

const createRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入描述', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

const createFormRef = ref()
const editFormRef = ref()
const uploadFormRef = ref()
const generateFormRef = ref()
const fileInput = ref()

onMounted(() => {
  loadKnowledgeBases()
  loadAvailableModels()
})

const loadKnowledgeBases = async () => {
  try {
    const response = await api.get('/knowledge/')
    knowledgeBases.value = response.data
  } catch (error) {
    ElMessage.error('加载知识库失败')
  }
}

const handleCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      creating.value = true
      try {
        await api.post('/knowledge/', createForm)
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadKnowledgeBases()
        // 重置表单
        createForm.title = ''
        createForm.description = ''
        createForm.category = 'ai'
      } catch (error) {
        ElMessage.error('创建失败')
      } finally {
        creating.value = false
      }
    }
  })
}

const handleCommand = async (command: string, kb: KnowledgeBase) => {
  switch (command) {
    case 'edit':
      // 编辑知识库
      editKnowledgeBase(kb)
      break
    case 'upload':
      // 上传文档
      uploadDocument(kb)
      break
    case 'delete':
      try {
        await ElMessageBox.confirm('确定要删除这个知识库吗？', '确认删除', {
          type: 'warning'
        })
        await api.delete(`/knowledge/${kb.id}/`)
        ElMessage.success('删除成功')
        loadKnowledgeBases()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
      break
  }
}

const viewKnowledgeBase = (kb: KnowledgeBase) => {
  // 查看知识库详情
  console.log('查看知识库:', kb)
}

const getCategoryType = (category: string) => {
  const types: Record<string, string> = {
    'general': '',
    'legal': 'primary',
    'education': 'success',
    'healthcare': 'warning',
    'finance': 'danger',
    'technology': 'info',
    'business': 'primary',
    'science': 'success',
    'humanities': 'warning',
    'engineering': 'danger',
    'arts': 'info',
    'other': ''
  }
  return types[category] || ''
}

const getCategoryName = (category: string) => {
  const names: Record<string, string> = {
    'general': '通用',
    'legal': '法律',
    'education': '教育',
    'healthcare': '医疗健康',
    'finance': '金融',
    'technology': '技术',
    'business': '商业',
    'science': '科学',
    'humanities': '人文社科',
    'engineering': '工程',
    'arts': '艺术设计',
    'other': '其他'
  }
  return names[category] || category
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// 编辑知识库
const editKnowledgeBase = (kb: KnowledgeBase) => {
  editForm.id = kb.id
  editForm.title = kb.title
  editForm.description = kb.description
  editForm.category = kb.category
  showEditDialog.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      editing.value = true
      try {
        await api.put(`/knowledge/${editForm.id}/`, {
          title: editForm.title,
          description: editForm.description,
          category: editForm.category
        })
        ElMessage.success('更新成功')
        showEditDialog.value = false
        loadKnowledgeBases()
      } catch (error) {
        ElMessage.error('更新失败')
      } finally {
        editing.value = false
      }
    }
  })
}

// 上传文档
const uploadDocument = (kb: KnowledgeBase) => {
  uploadForm.knowledge_base_id = kb.id
  uploadForm.file = null
  uploadMode.value = 'file'
  showUploadDialog.value = true
}

const startJsonImport = (kb: KnowledgeBase) => {
  uploadForm.knowledge_base_id = kb.id
  uploadForm.file = null
  uploadMode.value = 'json'
  showUploadDialog.value = true
}

const handleFileChange = (file: any) => {
  if (file && file.raw) {
    // 检查文件大小（10MB限制）
    const maxFileSize = 10 * 1024 * 1024 // 10MB
    if (file.raw.size > maxFileSize) {
      ElMessage.error(`文件大小不能超过10MB，当前文件大小：${(file.raw.size / 1024 / 1024).toFixed(2)}MB`)
      return
    }
    
    uploadForm.file = file.raw
    console.log('选择的文件:', file.name, '大小:', (file.raw.size / 1024 / 1024).toFixed(2) + 'MB')
  }
}

const handleJsonFileChange = (file: any) => {
  if (file && file.raw) {
    const maxFileSize = 100 * 1024 * 1024 // 100MB
    if (file.raw.size > maxFileSize) {
      ElMessage.error(`JSON 文件不能超过100MB，当前大小：${(file.raw.size / 1024 / 1024).toFixed(2)}MB`)
      return
    }
    uploadForm.file = file.raw
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleSimpleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    
    // 检查文件大小（10MB限制）
    const maxFileSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxFileSize) {
      ElMessage.error(`文件大小不能超过10MB，当前文件大小：${(file.size / 1024 / 1024).toFixed(2)}MB`)
      return
    }
    
    uploadForm.file = file
    console.log('选择的文件:', file.name, '大小:', (file.size / 1024 / 1024).toFixed(2) + 'MB')
  }
}

const handleUpload = async () => {
  if (!uploadForm.file) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  uploading.value = true
  try {
    // 先分析文档内容
    const content = await readFileContent(uploadForm.file)
    const analysisResult = await analyzeDocumentContent(content, uploadForm.file.name)
    
    // 如果文档不相关，显示警告并询问是否继续
    if (analysisResult.relevance === 'irrelevant') {
      const confirmed = await showAnalysisDialog(analysisResult)
      if (!confirmed) {
        uploading.value = false
        return
      }
    }
    
    // 如果文档质量较低，显示警告
    if (analysisResult.quality_score < 50) {
      ElMessage.warning(`文档质量较低（${analysisResult.quality_score.toFixed(1)}分），建议改进后再上传`)
    }

    const formData = new FormData()
    formData.append('file', uploadForm.file)

    // 注意：不要手动设置 Content-Type，让浏览器自动设置（包含 boundary）
    const response = await api.post(`/knowledge/${uploadForm.knowledge_base_id}/documents/`, formData)
    
    // 显示分析结果
    if (response.data.warning) {
      ElMessage.warning(response.data.warning)
    } else {
      ElMessage.success('上传成功')
    }
    
    showUploadDialog.value = false
    loadKnowledgeBases()
  } catch (error: any) {
    console.error('上传失败:', error)
    if (error.response && error.response.data) {
      if (error.response.data.analysis) {
        // 显示详细的分析结果
        await showAnalysisDialog(error.response.data.analysis, true)
      } else if (error.response.data.error) {
        // 显示后端返回的错误信息
        ElMessage.error(`上传失败: ${error.response.data.error}`)
        if (error.response.data.detail) {
          console.error('错误详情:', error.response.data.detail)
        }
      } else {
        ElMessage.error(`上传失败: ${JSON.stringify(error.response.data)}`)
      }
    } else {
      ElMessage.error('上传失败，请检查网络连接')
    }
  } finally {
    uploading.value = false
  }
}

const handleJsonImport = async () => {
  if (!uploadForm.knowledge_base_id) {
    ElMessage.error('请选择知识库')
    return
  }

  if (!uploadForm.file) {
    ElMessage.error('请先选择 JSON 文件')
    return
  }

  const formData = new FormData()
  formData.append('file', uploadForm.file)

  try {
    jsonUploading.value = true
    const response = await api.post(
      `/knowledge/knowledge-bases/${uploadForm.knowledge_base_id}/import-json/`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30 * 1000 // 30秒超时，因为这是创建任务，不是执行任务
      }
    )
    
    // 获取任务ID并开始轮询
    currentImportJobId.value = response.data.job_id
    showUploadDialog.value = false
    showImportProgressDialog.value = true
    startImportProgressPolling(uploadForm.knowledge_base_id, response.data.job_id)
    
    ElMessage.success('JSON 导入任务已创建，正在后台处理...')
  } catch (error: any) {
    console.error('JSON 导入失败:', error)
    ElMessage.error(
      error?.response?.data?.error ||
      'JSON 导入失败，请检查文件结构或稍后重试'
    )
  } finally {
    jsonUploading.value = false
  }
}

const startImportProgressPolling = (kbId: string, jobId: string) => {
  // 清除之前的轮询
  if (importProgressInterval.value) {
    clearInterval(importProgressInterval.value)
  }

  // 立即查询一次
  fetchImportProgress(kbId, jobId)

  // 每2秒轮询一次
  importProgressInterval.value = window.setInterval(() => {
    fetchImportProgress(kbId, jobId)
  }, 2000)
}

const fetchImportProgress = async (kbId: string, jobId: string) => {
  try {
    const response = await api.get(
      `/knowledge/knowledge-bases/${kbId}/import-jobs/${jobId}/`
    )
    const data = response.data
    
    importProgress.value = {
      status: data.status,
      total: data.total_documents || 0,
      created: data.created_documents || 0,
      vectorized: data.vectorized_documents || 0,
      skipped: data.skipped_documents || 0,
      percentage: data.progress_percentage || 0
    }

    // 如果任务完成，停止轮询
    if (['SUCCEEDED', 'FAILED', 'CANCELED'].includes(data.status)) {
      if (importProgressInterval.value) {
        clearInterval(importProgressInterval.value)
        importProgressInterval.value = null
      }

      if (data.status === 'SUCCEEDED') {
        ElMessage.success(`导入完成：成功 ${data.created_documents} 条，跳过 ${data.skipped_documents} 条`)
        loadKnowledgeBases()
        if (selectedKB.value?.id === kbId) {
          await loadDocuments(kbId)
        }
      } else if (data.status === 'FAILED') {
        ElMessage.error(`导入失败：${data.error_message || '未知错误'}`)
      }

      // 3秒后自动关闭对话框
      setTimeout(() => {
        showImportProgressDialog.value = false
        currentImportJobId.value = null
      }, 3000)
    }
  } catch (error: any) {
    console.error('查询导入进度失败:', error)
  }
}

const cancelImportJob = async () => {
  if (!currentImportJobId.value || !uploadForm.knowledge_base_id) {
    return
  }

  try {
    await api.post(
      `/knowledge/knowledge-bases/${uploadForm.knowledge_base_id}/import-jobs/${currentImportJobId.value}/cancel/`
    )
    ElMessage.info('已取消导入任务')
    if (importProgressInterval.value) {
      clearInterval(importProgressInterval.value)
      importProgressInterval.value = null
    }
    showImportProgressDialog.value = false
    currentImportJobId.value = null
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.error || '取消任务失败')
  }
}

// 获取导入状态类型
const getImportStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'PENDING': 'info',
    'PROCESSING': 'primary',
    'SUCCEEDED': 'success',
    'FAILED': 'danger',
    'CANCELED': 'warning'
  }
  return statusMap[status] || 'info'
}

// 获取导入状态文本
const getImportStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'PENDING': '待处理',
    'PROCESSING': '处理中',
    'SUCCEEDED': '成功',
    'FAILED': '失败',
    'CANCELED': '已取消'
  }
  return statusMap[status] || status
}

// 清理轮询
onUnmounted(() => {
  if (importProgressInterval.value) {
    clearInterval(importProgressInterval.value)
  }
})

// 读取文件内容
const readFileContent = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      let content = e.target?.result as string
      // 清理文件内容，移除问题字符
      if (content) {
        content = cleanFileContent(content)
      }
      resolve(content)
    }
    reader.onerror = reject
    reader.readAsText(file, 'UTF-8')
  })
}

// 清理文件内容
const cleanFileContent = (content: string): string => {
  // 过滤掉 NUL 字符和其他控制字符
  return content
    .replace(/\x00/g, '')  // 移除 NUL 字符
    .replace(/[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]/g, ' ')  // 移除其他控制字符，替换为空格
    .replace(/\s+/g, ' ')  // 合并多个空白字符
    .trim()  // 去除首尾空白
}

// 分析文档内容
const analyzeDocumentContent = async (content: string, filename: string) => {
  try {
    const response = await api.post('/knowledge/analyze-document/', {
      content,
      filename
    })
    return response.data
  } catch (error) {
    console.error('文档分析失败:', error)
    return {
      relevance: 'unknown',
      content_type: 'unknown',
      confidence: 0,
      quality_score: 0,
      keywords: [],
      issues: ['分析失败'],
      suggestions: ['请检查文档格式']
    }
  }
}

// 显示分析结果对话框
const showAnalysisDialog = (analysis: AnalysisPayload, isError = false): Promise<boolean> => {
  return new Promise((resolve) => {
    const relevanceText: Record<string, string> = {
      'highly_relevant': '高度相关',
      'relevant': '相关',
      'partially_relevant': '部分相关',
      'irrelevant': '不相关',
      'unknown': '未知'
    }
    
    const contentTypeText: Record<string, string> = {
      'educational': '教育内容',
      'technical': '技术文档',
      'research': '研究论文',
      'tutorial': '教程指南',
      'reference': '参考资料',
      'personal': '个人文档',
      'spam': '垃圾内容',
      'unknown': '未知类型'
    }

    const message = isError ? '文档上传被拒绝' : '文档分析结果'
    const type = isError ? 'error' : 'warning'
    
    ElMessageBox({
      title: message,
      message: `
        <div style="text-align: left;">
          <p><strong>相关性：</strong>${relevanceText[analysis.relevance] || analysis.relevance}</p>
          <p><strong>内容类型：</strong>${contentTypeText[analysis.content_type] || analysis.content_type}</p>
          <p><strong>质量分数：</strong>${analysis.quality_score.toFixed(1)}/100</p>
          <p><strong>置信度：</strong>${(analysis.confidence * 100).toFixed(1)}%</p>
          ${analysis.issues.length > 0 ? `<p><strong>问题：</strong></p><ul>${analysis.issues.map(issue => `<li>${issue}</li>`).join('')}</ul>` : ''}
          ${analysis.suggestions.length > 0 ? `<p><strong>建议：</strong></p><ul>${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}</ul>` : ''}
        </div>
      `,
      type,
      dangerouslyUseHTMLString: true,
      showCancelButton: !isError,
      confirmButtonText: isError ? '确定' : '继续上传',
      cancelButtonText: '取消上传'
    }).then(() => {
      resolve(true)
    }).catch(() => {
      resolve(false)
    })
  })
}

const goBack = () => {
  router.push('/')
}

// 学习内容相关方法
const generateLearningContent = async (kb: KnowledgeBase) => {
  selectedKB.value = kb
  showGenerateDialog.value = true
}

const viewLearningContent = async (kb: KnowledgeBase) => {
  selectedKB.value = kb
  showLearningContentDialog.value = true
  await loadLearningContent(kb.id)
}

const loadLearningContent = async (knowledgeBaseId: string) => {
  try {
    const response = await api.get(`/learning/knowledge-bases/${knowledgeBaseId}/content/`)
    learningContents.value = response.data.contents || []
    
    // 设置默认激活的标签页
    if (learningContents.value.length > 0) {
      activeTab.value = learningContents.value[0].content_type
    }
    
  } catch (error: any) {
    ElMessage.error('加载学习内容失败')
    learningContents.value = []
  }
}


const handleLearningContentClose = () => {
  showLearningContentDialog.value = false
  selectedKB.value = null
  learningContents.value = []
  activeTab.value = 'summary'
}

// 文档查看相关方法
const viewDocuments = async (kb: KnowledgeBase) => {
  selectedKB.value = kb
  showDocumentsDialog.value = true
  await loadDocuments(kb.id)
}

const loadDocuments = async (knowledgeBaseId: string) => {
  try {
    const response = await api.get(`/knowledge/${knowledgeBaseId}/documents/`)
    documents.value = response.data || []
  } catch (error: any) {
    ElMessage.error("加载文档失败")
    documents.value = []
  }
}

const viewDocumentContent = (doc: any) => {
  selectedDocument.value = doc
  showDocumentContentDialog.value = true
}

const deleteDocument = async (doc: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${doc.title}" 吗？`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    )
    
    await api.delete(`/knowledge/${selectedKB.value?.id}/documents/${doc.id}/`)
    ElMessage.success("文档删除成功")
    if (selectedKB.value?.id) {
      await loadDocuments(selectedKB.value.id)
    }
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error("删除文档失败")
    }
  }
}

const handleDocumentsClose = () => {
  showDocumentsDialog.value = false
  selectedKB.value = null
  documents.value = []
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return "0 B"
  const k = 1024
  const sizes = ["B", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

// AI内容生成相关方法
const loadAvailableModels = async () => {
  try {
    const response = await api.get('/learning/ai-models/')
    availableModels.value = Object.entries(response.data).map(([id, model]: [string, any]) => ({
      id,
      name: model.name,
      description: model.description,
      max_tokens: model.max_tokens,
      supported_types: model.supported_types,
      available: true // 假设都可用，实际应该检查API密钥配置
    }))
  } catch (error) {
    console.error('加载AI模型失败:', error)
    // 提供默认模型
    availableModels.value = [
      { id: 'deepseek', name: 'DeepSeek', description: '深度求索大模型', available: false },
      { id: 'qwen', name: '通义千问', description: '阿里云大模型', available: false },
      { id: 'glm', name: '智谱AI', description: '清华智谱大模型', available: false }
    ]
  }
}

const handleGenerate = async () => {
  if (!generateFormRef.value) return

  await generateFormRef.value.validate(async (valid: boolean) => {
    if (valid && selectedKB.value) {
      generating.value = true
      generationProgress.value = 0
      generationStatus.value = 'active'
      generationText.value = '正在生成相关内容...'

      try {
        const response = await api.post(`/learning/knowledge-bases/${selectedKB.value.id}/generate-content/`, {
          content_types: generateForm.content_types,
          ai_model: generateForm.ai_model,
          config: generateForm.config
        })

        // 模拟进度更新
        const progressInterval = setInterval(() => {
          if (generationProgress.value < 90) {
            generationProgress.value += Math.random() * 20
          }
        }, 500)

        // 等待生成完成
        await new Promise(resolve => setTimeout(resolve, 3000))

        clearInterval(progressInterval)
        generationProgress.value = 100
        generationStatus.value = 'success'
        generationText.value = '生成完成！'

        ElMessage.success(`成功生成 ${response.data.total_generated} 种学习内容`)

        // 关闭对话框并刷新内容
        setTimeout(() => {
          handleGenerateClose()
          if (showLearningContentDialog.value) {
            loadLearningContent(selectedKB.value.id)
          }
        }, 1000)

      } catch (error: any) {
        generationStatus.value = 'exception'
        generationText.value = '生成失败'
        ElMessage.error(error.response?.data?.error || '生成相关内容失败')
      } finally {
        generating.value = false
      }
    }
  })
}

const handleGenerateClose = () => {
  showGenerateDialog.value = false
  selectedKB.value = null
  generating.value = false
  generationProgress.value = 0
  generationStatus.value = 'active'
  generationText.value = ''
  
  // 重置表单
  generateForm.ai_model = 'deepseek'
  generateForm.content_types = ['summary', 'outline', 'key_concepts', 'q_and_a']
  generateForm.config.max_tokens = 2000
  generateForm.config.temperature = 0.7
}
</script>

<style scoped>
.knowledge-container {
  min-height: 100vh;
  background: var(--apple-body-bg);
  padding: 32px 48px 64px;
}

.knowledge-header {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-card-radius);
  padding: 0;
  height: 90px;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-button {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-control-radius);
  padding: 8px;
  color: var(--apple-text-primary);
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
}

.back-button:hover {
  background: rgba(10, 132, 255, 0.08);
  border-color: var(--apple-brand-blue);
  color: var(--apple-brand-blue);
}

.header-title h2 {
  color: var(--apple-text-primary);
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-title p {
  margin: 0;
  color: var(--apple-text-secondary);
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.create-button {
  border-radius: var(--apple-pill-radius);
  padding: 12px 24px;
  font-weight: 500;
}

.knowledge-main {
  flex: 1;
  padding: 0;
  overflow: visible;
}

.knowledge-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.kb-card {
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
  border: 1px solid var(--apple-border);
  border-radius: 20px;
  background: var(--apple-surface);
  overflow: hidden;
}

.kb-card:hover {
  border-color: var(--apple-brand-blue);
  transform: translateY(-3px);
}

/* 知识库卡片头部 */
.kb-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  padding-bottom: 1rem;
}

.kb-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #0a84ff 0%, #5e5ce6 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.kb-info {
  flex: 1;
  min-width: 0;
}

.kb-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.kb-description {
  color: var(--apple-text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.more-button {
  color: var(--apple-text-secondary);
  padding: 4px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.more-button:hover {
  background: var(--apple-overlay);
  color: var(--apple-brand-blue);
}

/* 知识库卡片元数据 */
.kb-meta {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.kb-tags {
  display: flex;
  gap: 0.5rem;
}

.kb-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--apple-text-secondary);
  font-size: 0.85rem;
}

.kb-count {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.kb-date {
  font-size: 0.8rem;
  color: #a1a1a6;
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.kb-header h3 {
  color: #2c3e50;
  margin: 0;
  flex: 1;
}

.kb-description {
  color: #7f8c8d;
  margin-bottom: 16px;
  line-height: 1.5;
}

.kb-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.kb-count {
  margin: 0 8px;
}

.kb-date {
  color: #ccc;
}

.kb-actions {
  margin-top: 8px;
  padding: 0 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* 学习内容样式 */
.empty-content {
  text-align: center;
  padding: 40px;
}

.learning-content {
  max-height: 600px;
  overflow-y: auto;
}

.content-display {
  padding: 20px;
}


.no-data {
  text-align: center;
  color: #909399;
  padding: 40px;
  font-size: 14px;
}

/* 按钮样式优化 */
.action-btn {
  border-radius: var(--apple-pill-radius) !important;
  font-weight: 500 !important;
  border: 1px solid var(--apple-border) !important;
  color: var(--apple-text-primary) !important;
  background: transparent !important;
  box-shadow: none !important;
}

.action-btn:hover {
  border-color: var(--apple-brand-blue) !important;
  color: var(--apple-brand-blue) !important;
}

.generate-btn {
  background: var(--apple-success) !important;
  border-color: var(--apple-success) !important;
  color: #fff !important;
}


.summary-content h4 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.summary-section {
  margin-bottom: 24px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.summary-section h5 {
  color: #409eff;
  margin-bottom: 12px;
}

.key-points {
  margin-top: 12px;
}

.key-points h6 {
  color: #606266;
  margin-bottom: 8px;
}

.key-points ul {
  margin: 0;
  padding-left: 20px;
}

.key-points li {
  margin-bottom: 4px;
  color: #606266;
}

.outline-content h4 {
  color: #2c3e50;
  margin-bottom: 16px;
}

.chapter-item {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: white;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.chapter-number {
  width: 32px;
  height: 32px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.chapter-header h5 {
  margin: 0;
  flex: 1;
  color: #2c3e50;
}

.chapter-time {
  color: #999;
  font-size: 14px;
}

.key-topics {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.concepts-content h4 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.concepts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.concept-card {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.concept-card h5 {
  color: #409eff;
  margin-bottom: 8px;
}

.concept-card p {
  color: #606266;
  margin-bottom: 12px;
}

.related-docs {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.related-docs span {
  color: #999;
  font-size: 14px;
}

.qa-content h4 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.qa-item {
  margin-bottom: 24px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.qa-item h5 {
  color: #409eff;
  margin-bottom: 12px;
}

.answer {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

.qa-source {
  margin-top: 8px;
}

/* 文档查看样式 */
.empty-documents {
  text-align: center;
  padding: 40px;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
}

.json-tip {
  font-size: 12px;
  color: #606266;
  background: #f8f9fb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  line-height: 1.4;
}

.json-tip pre {
  background: #111827;
  color: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0 0;
  font-size: 12px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.dialog-header span {
  font-size: 18px;
  font-weight: 500;
  color: #2c3e50;
}

.documents-list {
  max-height: 600px;
  overflow-y: auto;
}

.document-item {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.document-header h4 {
  margin: 0;
  color: #2c3e50;
  flex: 1;
}

.document-actions {
  display: flex;
  gap: 8px;
}

.document-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.document-size,
.document-date {
  color: #999;
}

.document-preview {
  color: #606266;
  line-height: 1.6;
}

.document-preview p {
  margin: 0;
}

.document-content {
  flex: 1;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.document-content-dialog .el-dialog__body {
  padding: 20px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.document-content-dialog .el-dialog {
  max-height: 90vh;
}

.document-content-dialog .el-dialog__header {
  flex-shrink: 0;
}

/* 强制防止文字溢出 */
.document-content-dialog * {
  max-width: 100% !important;
  box-sizing: border-box !important;
}

.document-content-dialog .el-dialog__body {
  overflow: hidden !important;
}

.document-content-dialog .document-content {
  overflow: hidden !important;
}

.document-content-dialog .document-text {
  overflow: hidden !important;
}

.document-content-dialog .document-text pre {
  overflow: hidden !important;
  white-space: pre-wrap !important;
  word-break: break-all !important;
}

.document-info {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.document-text {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden !important;
  min-height: 0;
  position: relative;
}

.document-text pre {
  margin: 0;
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  word-break: break-all !important;
  font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #2c3e50;
  max-width: 100% !important;
  width: 100% !important;
  overflow-x: hidden !important;
  overflow-wrap: break-word !important;
  hyphens: auto;
  box-sizing: border-box !important;
  padding: 0;
  display: block;
}

/* 上传组件样式 */
:deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

:deep(.el-upload:hover) {
  border-color: #409eff;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

:deep(.el-icon--upload) {
  font-size: 67px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

:deep(.el-upload__text) {
  color: #606266;
  font-size: 14px;
  text-align: center;
}

:deep(.el-upload__text em) {
  color: #409eff;
  font-style: normal;
}

/* 文件上传容器样式 */
.file-upload-container {
  width: 100%;
}

.simple-file-input {
  margin-top: 16px;
  padding: 16px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  text-align: center;
  background-color: #fafafa;
}

.selected-file {
  display: block;
  margin-top: 8px;
  color: #409eff;
  font-size: 14px;
}

/* 知识库操作按钮样式 */
.kb-actions {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 120px;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.action-btn:hover::before {
  left: 100%;
}

.action-btn .el-icon {
  margin-right: 6px;
  font-size: 16px;
}

/* 特殊按钮样式 */
.generate-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
  color: white !important;
  border: none !important;
  font-weight: 600 !important;
}

.generate-btn:hover {
  background: linear-gradient(135deg, #ff5252 0%, #e53e3e 100%) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4) !important;
}

/* AI内容生成对话框样式 */
.generate-content {
  padding: 20px 0;
}

.kb-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.kb-info h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.kb-info p {
  margin: 0 0 12px 0;
  color: #6c757d;
  line-height: 1.5;
}

.kb-stats {
  display: flex;
  gap: 12px;
  align-items: center;
}

.doc-count {
  color: #6c757d;
  font-size: 14px;
}

.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.generation-progress {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.progress-text {
  text-align: center;
  margin-top: 12px;
  color: #6c757d;
  font-size: 14px;
}

/* JSON 导入进度对话框样式 */
.import-progress-content {
  padding: 20px 0;
}

.progress-stats {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-primary {
  color: #409eff;
  font-weight: 500;
}

.text-warning {
  color: #e6a23c;
  font-weight: 500;
}

/* 生成对话框样式 */
.generate-dialog .el-dialog__header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0;
  margin: 0;
  padding: 20px 24px;
}

.generate-dialog .el-dialog__title {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.generate-dialog .el-dialog__headerbtn .el-dialog__close {
  color: white;
}

.kb-info-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e0e0e0;
}

.kb-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.kb-icon {
  margin-right: 12px;
  color: #409eff;
}

.kb-details h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.kb-details p {
  margin: 0;
  color: #6c757d;
  font-size: 14px;
}

.kb-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

.feature-description {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.feature-description h5 {
  margin: 0 0 8px 0;
  color: #1976d2;
  font-size: 16px;
  font-weight: 600;
}

.feature-description p {
  margin: 0;
  color: #424242;
  font-size: 14px;
  line-height: 1.5;
}

.content-types-section {
  margin-top: 8px;
}

.section-description {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
}

.content-types-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.content-type-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.content-type-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.content-type-item .el-checkbox {
  width: 100%;
  margin: 0;
  padding: 16px;
}

.content-type-item .el-checkbox__label {
  width: 100%;
  padding: 0;
}

.type-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.type-icon {
  font-size: 24px;
  width: 32px;
  text-align: center;
}

.type-info {
  flex: 1;
}

.type-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.type-desc {
  font-size: 12px;
  color: #909399;
}

.generate-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  font-weight: 600 !important;
  padding: 12px 24px !important;
  position: relative !important;
  overflow: hidden !important;
}

.generate-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s;
}

.generate-button:hover::before {
  left: 100%;
}

.generate-button:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4c93 100%) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
  }
  
  .action-btn {
    min-width: auto;
    width: 100%;
  }
  
  .content-types-grid {
    grid-template-columns: 1fr;
  }
  
  .kb-stats {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
