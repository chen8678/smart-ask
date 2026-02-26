<template>
  <div class="courses-container">
    <!-- 顶部导航 -->
    <el-header class="courses-header">
      <div class="header-content">
        <h2>私有课程管理</h2>
        <div class="header-actions">
          <el-button type="success" @click="showGenerateDialog = true">
            <el-icon><Magic /></el-icon>
            AI生成课程
          </el-button>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            手动创建
          </el-button>
          <el-button type="info" @click="showTemplateDialog = true">
            <el-icon><Document /></el-icon>
            课程模板
          </el-button>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="courses-main">
      <div class="courses-list">
        <el-card
          v-for="course in courses"
          :key="course.id"
          class="course-card"
          @click="viewCourse(course)"
        >
          <div class="course-header">
            <h3>{{ course.title }}</h3>
            <div class="course-tags">
              <el-tag :type="getDifficultyType(course.difficulty_level)">
                {{ getDifficultyName(course.difficulty_level) }}
              </el-tag>
              <el-tag :type="getStatusType(course.status)">
                {{ getStatusName(course.status) }}
              </el-tag>
            </div>
          </div>
          <p class="course-description">{{ course.description }}</p>
          <div class="course-meta">
            <span class="course-instructor">讲师: {{ course.instructor_name }}</span>
            <span class="course-hours">{{ course.estimated_hours }}小时</span>
            <span class="course-date">{{ formatDate(course.created_at) }}</span>
          </div>
          <div class="course-actions">
            <el-button 
              v-if="course.instructor === currentUserId && course.status === 'draft'"
              type="success" 
              @click.stop="publishCourse(course)"
            >
              发布课程
            </el-button>
            <el-button 
              v-if="course.instructor === currentUserId"
              type="danger" 
              @click.stop="deleteCourse(course)"
            >
              删除课程
            </el-button>
            <el-button 
              type="primary" 
              @click.stop="viewCourse(course)"
            >
              查看详情
            </el-button>
            <el-button 
              v-if="course.instructor === currentUserId"
              type="info" 
              @click.stop="editCourse(course)"
            >
              编辑课程
            </el-button>
          </div>
          
          <!-- 课程特色标签 -->
          <div class="course-features">
            <el-tag v-if="course.knowledge_base_name" type="info" size="small">
              <el-icon><Document /></el-icon>
              基于知识库: {{ course.knowledge_base_name }}
            </el-tag>
            <el-tag v-if="course.chapter_count > 0" type="success" size="small">
              <el-icon><List /></el-icon>
              {{ course.chapter_count }}个章节
            </el-tag>
            <el-tag v-if="course.mind_map_data" type="primary" size="small">
              <el-icon><Share /></el-icon>
              思维导图
            </el-tag>
            <el-tag v-if="course.generated_content && Object.keys(course.generated_content).length > 0" type="warning" size="small">
              <el-icon><Magic /></el-icon>
              AI生成内容
            </el-tag>
          </div>
          
          <!-- 课程统计信息 -->
          <div class="course-stats">
            <div class="stat-item">
              <el-icon><Clock /></el-icon>
              <span>预计{{ course.estimated_hours }}小时</span>
            </div>
            <div class="stat-item">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatDate(course.created_at) }}</span>
            </div>
            <div v-if="course.updated_at !== course.created_at" class="stat-item">
              <el-icon><Edit /></el-icon>
              <span>更新于{{ formatDate(course.updated_at) }}</span>
            </div>
            <div class="stat-item" v-if="course.view_count > 0">
              <el-icon><View /></el-icon>
              <span>{{ course.view_count }}次浏览</span>
            </div>
          </div>
        </el-card>
      </div>
    </el-main>

    <!-- AI生成课程对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="AI生成课程"
      width="600px"
    >
      <el-form
        ref="generateFormRef"
        :model="generateForm"
        :rules="generateRules"
        label-width="100px"
      >
        <el-form-item label="知识库" prop="knowledge_base_id">
          <el-select 
            v-model="generateForm.knowledge_base_id" 
            placeholder="请选择知识库"
            style="width: 100%"
            @change="onKnowledgeBaseChange"
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.title"
              :value="kb.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="课程标题" prop="title">
          <el-input v-model="generateForm.title" placeholder="请输入课程标题" />
        </el-form-item>
        
        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="generateForm.description"
            type="textarea"
            placeholder="AI将基于知识库内容自动生成描述"
            :rows="3"
          />
        </el-form-item>
        
        <el-form-item label="难度级别" prop="difficulty_level">
          <el-select v-model="generateForm.difficulty_level" placeholder="请选择难度">
            <el-option label="基础概念 - 简单易懂" :value="1" />
            <el-option label="深入原理 - 适中难度" :value="2" />
            <el-option label="复杂应用 - 专业深度" :value="3" />
            <el-option label="前沿研究 - 专家级别" :value="4" />
          </el-select>
        </el-form-item>
        
        <!-- 知识库信息预览 -->
        <el-form-item v-if="selectedKnowledgeBase" label="知识库信息">
          <el-card class="knowledge-base-preview">
            <div class="kb-info">
              <h4>{{ selectedKnowledgeBase.title }}</h4>
              <p>{{ selectedKnowledgeBase.description }}</p>
              <div class="kb-stats">
                <el-tag type="info">{{ selectedKnowledgeBase.document_count }}个文档</el-tag>
                <el-tag type="success">{{ selectedKnowledgeBase.category }}</el-tag>
              </div>
            </div>
          </el-card>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button 
          type="success" 
          @click="handleGenerate" 
          :loading="generating"
          :disabled="!generateForm.knowledge_base_id"
        >
          <el-icon><Magic /></el-icon>
          AI生成课程
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建课程对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="手动创建课程"
      width="500px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入课程标题" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入课程描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="createForm.category" placeholder="请选择分类">
            <el-option label="人工智能" value="ai" />
            <el-option label="机器学习" value="ml" />
            <el-option label="深度学习" value="dl" />
            <el-option label="自然语言处理" value="nlp" />
            <el-option label="计算机视觉" value="cv" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度" prop="difficulty_level">
          <el-select v-model="createForm.difficulty_level" placeholder="请选择难度">
            <el-option label="基础概念 - 简单易懂" :value="1" />
            <el-option label="深入原理 - 适中难度" :value="2" />
            <el-option label="复杂应用 - 专业深度" :value="3" />
            <el-option label="前沿研究 - 专家级别" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长" prop="estimated_hours">
          <el-input-number
            v-model="createForm.estimated_hours"
            :min="1"
            :max="1000"
            placeholder="预计学习时长（小时）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 课程模板对话框 -->
    <el-dialog
      v-model="showTemplateDialog"
      title="课程模板"
      width="800px"
    >
      <div class="template-grid">
        <div 
          v-for="template in courseTemplates" 
          :key="template.id"
          class="template-card"
          @click="useTemplate(template)"
        >
          <div class="template-header">
            <h4>{{ template.name }}</h4>
            <el-tag :type="template.category === 'ai' ? 'primary' : 'success'">
              {{ template.category === 'ai' ? 'AI相关' : '通用' }}
            </el-tag>
          </div>
          <p class="template-description">{{ template.description }}</p>
          <div class="template-features">
            <el-tag 
              v-for="feature in template.features" 
              :key="feature"
              size="small"
              type="info"
            >
              {{ feature }}
            </el-tag>
          </div>
          <div class="template-stats">
            <span>{{ template.chapters }}个章节</span>
            <span>{{ template.estimated_hours }}小时</span>
          </div>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const router = useRouter()
const authStore = useAuthStore()

interface Course {
  id: string
  title: string
  description: string
  category: string
  difficulty_level: number
  estimated_hours: number
  instructor: string
  instructor_name: string
  status: string
  knowledge_base?: string
  knowledge_base_name?: string
  chapter_count?: number
  created_at: string
  updated_at: string
}

interface KnowledgeBase {
  id: string
  name: string
  description: string
  document_count: number
  total_size: number
}

const courses = ref<Course[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const showCreateDialog = ref(false)
const showGenerateDialog = ref(false)
const showTemplateDialog = ref(false)
const creating = ref(false)
const generating = ref(false)
const currentUserId = ref('')
const selectedCourse = ref<Course | null>(null)

// 课程模板数据
const courseTemplates = ref([
  {
    id: 'ai-basics',
    name: '人工智能基础课程',
    description: '从零开始学习人工智能的基本概念、发展历程和核心算法',
    category: 'ai',
    chapters: 8,
    estimated_hours: 20,
    features: ['基础概念', '机器学习', '深度学习', '实践项目']
  },
  {
    id: 'machine-learning',
    name: '机器学习实战课程',
    description: '深入学习机器学习算法，包括监督学习、无监督学习和强化学习',
    category: 'ai',
    chapters: 12,
    estimated_hours: 30,
    features: ['算法原理', '代码实现', '项目实战', '模型优化']
  },
  {
    id: 'nlp-course',
    name: '自然语言处理课程',
    description: '掌握NLP核心技术，包括文本预处理、词向量、语言模型等',
    category: 'ai',
    chapters: 10,
    estimated_hours: 25,
    features: ['文本处理', '词向量', '语言模型', '情感分析']
  },
  {
    id: 'computer-vision',
    name: '计算机视觉课程',
    description: '学习图像处理、目标检测、图像分类等计算机视觉技术',
    category: 'ai',
    chapters: 9,
    estimated_hours: 22,
    features: ['图像处理', '卷积神经网络', '目标检测', '图像生成']
  },
  {
    id: 'data-science',
    name: '数据科学入门课程',
    description: '数据科学基础课程，涵盖数据分析、可视化、统计学习等',
    category: 'general',
    chapters: 6,
    estimated_hours: 15,
    features: ['数据分析', '数据可视化', '统计学习', '数据挖掘']
  }
])

const createForm = reactive({
  title: '',
  description: '',
  category: 'ai',
  difficulty_level: 1,
  estimated_hours: 10
})

const generateForm = reactive({
  knowledge_base_id: '',
  title: '',
  description: '',
  difficulty_level: 1
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
  ],
  difficulty_level: [
    { required: true, message: '请选择难度', trigger: 'change' }
  ],
  estimated_hours: [
    { required: true, message: '请输入时长', trigger: 'blur' }
  ]
}

const generateRules = {
  knowledge_base_id: [
    { required: true, message: '请选择知识库', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入课程标题', trigger: 'blur' }
  ],
  difficulty_level: [
    { required: true, message: '请选择难度', trigger: 'change' }
  ]
}


const createFormRef = ref()
const generateFormRef = ref()

// 计算属性：选中的知识库
const selectedKnowledgeBase = computed(() => {
  return knowledgeBases.value.find(kb => kb.id === generateForm.knowledge_base_id)
})

onMounted(() => {
  loadCourses()
  loadKnowledgeBases()
  // 获取当前用户ID
  if (authStore.user) {
    currentUserId.value = authStore.user.id
  }
})

const loadCourses = async () => {
  try {
    const response = await api.get('/learning/courses/')
    courses.value = response.data
  } catch (error) {
    ElMessage.error('加载课程失败')
  }
}

const loadKnowledgeBases = async () => {
  try {
    const response = await api.get('/knowledge/')
    knowledgeBases.value = response.data
  } catch (error) {
    ElMessage.error('加载知识库失败')
  }
}

const onKnowledgeBaseChange = (knowledgeBaseId: string) => {
  const kb = knowledgeBases.value.find(k => k.id === knowledgeBaseId)
  if (kb && !generateForm.title) {
    // 自动生成课程标题
    generateForm.title = `基于${kb.title}的学习课程`
  }
}

const handleGenerate = async () => {
  if (!generateFormRef.value) return

  await generateFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      generating.value = true
      try {
        const response = await api.post('/learning/generate-course/', generateForm)
        ElMessage.success('课程生成成功！')
        showGenerateDialog.value = false
        loadCourses()
        
        // 重置表单
        generateForm.knowledge_base_id = ''
        generateForm.title = ''
        generateForm.description = ''
        generateForm.difficulty_level = 1
      } catch (error: any) {
        ElMessage.error(error.response?.data?.error || '课程生成失败')
      } finally {
        generating.value = false
      }
    }
  })
}

const handleCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      creating.value = true
      try {
        await api.post('/learning/courses/', createForm)
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadCourses()
        // 重置表单
        createForm.title = ''
        createForm.description = ''
        createForm.category = 'ai'
        createForm.difficulty_level = 1
        createForm.estimated_hours = 10
      } catch (error) {
        ElMessage.error('创建失败')
      } finally {
        creating.value = false
      }
    }
  })
}


const publishCourse = async (course: Course) => {
  try {
    await ElMessageBox.confirm('确定要发布这门课程吗？', '确认发布', {
      type: 'warning'
    })
    
    await api.post(`/learning/courses/${course.id}/publish/`)
    
    ElMessage.success('课程发布成功')
    loadCourses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败')
    }
  }
}


const editCourse = (course: Course) => {
  // 跳转到课程编辑页面（可以复用创建表单）
  createForm.title = course.title
  createForm.description = course.description
  createForm.category = course.category
  createForm.difficulty_level = course.difficulty_level
  createForm.estimated_hours = course.estimated_hours
  
  showCreateDialog.value = true
  // 这里可以添加编辑模式标识
}

const deleteCourse = async (course: Course) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${course.title}"吗？此操作不可恢复！`, 
      '确认删除', 
      {
        type: 'error',
        confirmButtonText: '删除',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await api.delete(`/learning/courses/${course.id}/delete/`)
    
    ElMessage.success('课程删除成功')
    loadCourses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewCourse = (course: Course) => {
  // 跳转到课程详情页面
  router.push(`/courses/${course.id}`)
}

const getDifficultyType = (level: number) => {
  const types = ['', 'success', 'warning', 'danger', 'info']
  return types[level] || ''
}

const getDifficultyName = (level: number) => {
  const names = ['', '初级', '中级', '高级', '专家']
  return names[level] || ''
}

const getStatusType = (status: string) => {
  const types = {
    'draft': 'info',
    'published': 'success',
    'archived': 'warning'
  }
  return types[status] || 'info'
}

const getStatusName = (status: string) => {
  const names = {
    'draft': '草稿',
    'published': '已发布',
    'archived': '已归档'
  }
  return names[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const goBack = () => {
  router.push('/')
}

// 使用课程模板
const useTemplate = (template: any) => {
  // 将模板数据填充到创建表单
  createForm.title = template.name
  createForm.description = template.description
  createForm.category = template.category
  createForm.estimated_hours = template.estimated_hours
  createForm.difficulty_level = 1 // 默认难度
  
  showTemplateDialog.value = false
  showCreateDialog.value = true
}

</script>

<style scoped>
.courses-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.courses-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h2 {
  color: #2c3e50;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.courses-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.courses-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.course-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f5f5f5;
}

.course-header h3 {
  color: #2c3e50;
  margin: 0;
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.course-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-left: 12px;
}

.course-description {
  color: #666;
  margin-bottom: 16px;
  line-height: 1.6;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #999;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.course-instructor {
  margin-right: 8px;
}

.course-hours {
  margin-right: 8px;
}

.course-date {
  color: #ccc;
}

.course-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.course-features {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.knowledge-base-preview {
  margin-top: 8px;
}

.kb-info h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.kb-info p {
  margin: 0 0 12px 0;
  color: #7f8c8d;
  font-size: 14px;
}

.kb-stats {
  display: flex;
  gap: 8px;
}

.course-actions .favorited {
  color: #f56c6c;
}

.course-actions .favorited:hover {
  color: #f56c6c;
  background-color: #fef0f0;
}

.course-stats {
  margin-top: 16px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.course-stats .stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.course-stats .stat-item .el-icon {
  font-size: 16px;
  color: #409eff;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.template-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.template-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.template-description {
  color: #7f8c8d;
  margin-bottom: 16px;
  line-height: 1.5;
  font-size: 14px;
}

.template-features {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.template-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.template-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>