<template>
  <div class="course-detail-container">
    <!-- 顶部导航 -->
    <el-header class="course-header">
      <div class="header-content">
        <div class="header-left">
          <el-button @click="goBack" circle>
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <h2>{{ course?.title || '课程详情' }}</h2>
        </div>
        <div class="header-actions">
          <el-button v-if="isInstructor" type="primary" @click="showCreateChapterDialog = true">
            <el-icon><Plus /></el-icon>
            添加章节
          </el-button>
          <el-button v-if="isInstructor && course?.status === 'draft'" type="success" @click="publishCourse">
            发布课程
          </el-button>
          <el-button v-if="isInstructor && course?.status === 'draft'" type="danger" @click="deleteCourse">
            删除课程
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="course-main">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="course" class="course-content">
        <!-- 课程信息卡片 -->
        <el-card class="course-info-card">
          <div class="course-info">
            <div class="course-basic">
              <h3>{{ course.title }}</h3>
              <p class="course-description">{{ course.description }}</p>
              <div class="course-meta">
                <el-tag :type="getDifficultyType(course.difficulty_level)">
                  {{ getDifficultyName(course.difficulty_level) }}
                </el-tag>
                <el-tag :type="getStatusType(course.status)">
                  {{ getStatusName(course.status) }}
                </el-tag>
                <span class="course-instructor">讲师: {{ course.instructor_name }}</span>
                <span class="course-hours">{{ course.estimated_hours }}小时</span>
              </div>
            </div>
            
            <!-- 思维导图按钮 -->
            <div class="mind-map-section">
              <el-button type="primary" @click="showMindMap = true">
                <el-icon><Share /></el-icon>
                {{ course.mind_map_data ? '查看思维导图' : '生成思维导图' }}
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 课程章节 -->
        <el-card class="chapters-card">
          <template #header>
            <div class="card-header">
              <h3>课程章节</h3>
              <span class="chapter-count">{{ course.chapter_count || 0 }}个章节</span>
            </div>
          </template>
          
          <div v-if="chapters.length === 0" class="empty-chapters">
            <el-empty description="暂无章节内容" />
          </div>
          
          <div v-else class="chapters-list">
            <div 
              v-for="(chapter, index) in chapters" 
              :key="chapter.id"
              class="chapter-item"
              @click="viewChapter(chapter)"
            >
              <div class="chapter-header">
                <div class="chapter-number">{{ index + 1 }}</div>
                <div class="chapter-info">
                  <h4>{{ chapter.title }}</h4>
                  <p class="chapter-summary">{{ chapter.summary }}</p>
                </div>
                <div class="chapter-meta">
                  <span class="chapter-duration">{{ chapter.estimated_minutes }}分钟</span>
                  <div class="chapter-actions">
                    <el-button type="text" @click.stop="viewChapter(chapter)">
                      查看详情
                    </el-button>
                    <el-button v-if="isInstructor" type="text" @click.stop="editChapter(chapter)">
                      编辑
                    </el-button>
                    <el-button v-if="isInstructor" type="text" @click.stop="deleteChapter(chapter)" class="delete-btn">
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
              
              <!-- 关键概念 -->
              <div v-if="chapter.key_concepts && chapter.key_concepts.length > 0" class="key-concepts">
                <el-tag 
                  v-for="concept in chapter.key_concepts.slice(0, 3)" 
                  :key="concept"
                  size="small"
                  type="info"
                >
                  {{ concept }}
                </el-tag>
                <el-tag v-if="chapter.key_concepts.length > 3" size="small" type="info">
                  +{{ chapter.key_concepts.length - 3 }}个概念
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 学习分析 -->
        <CourseAnalytics :course-id="courseId" />
      </div>
    </el-main>

    <!-- 思维导图对话框 -->
    <el-dialog
      v-model="showMindMap"
      :title="course?.title + ' - 思维导图'"
      width="90%"
      :before-close="handleMindMapClose"
      class="mind-map-dialog"
    >
      <MindMap 
        v-if="course?.mind_map_data" 
        :data="course.mind_map_data" 
        :title="course.title"
        :width="800"
        :height="600"
      />
      <div v-else class="mind-map-placeholder">
        <el-empty description="该课程暂无思维导图数据">
          <el-button type="primary" @click="generateMindMap" :loading="generatingMindMap">
            生成思维导图
          </el-button>
        </el-empty>
      </div>
    </el-dialog>

    <!-- 章节详情对话框 -->
    <el-dialog
      v-model="showChapterDetail"
      :title="selectedChapter?.title"
      width="70%"
    >
      <div v-if="selectedChapter" class="chapter-detail">
        <div class="chapter-content">
          <h4>章节摘要</h4>
          <p>{{ selectedChapter.summary }}</p>
          
          <h4>详细内容</h4>
          <div class="content-text">{{ selectedChapter.content }}</div>
          
          <div v-if="selectedChapter.key_concepts && selectedChapter.key_concepts.length > 0">
            <h4>关键概念</h4>
            <div class="concepts-list">
              <el-tag 
                v-for="concept in selectedChapter.key_concepts" 
                :key="concept"
                type="info"
                class="concept-tag"
              >
                {{ concept }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <div class="chapter-actions">
          <el-button type="primary" @click="markChapterComplete">
            标记为已完成
          </el-button>
          <el-button @click="showChapterDetail = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 章节创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateChapterDialog"
      :title="editingChapter ? '编辑章节' : '创建章节'"
      width="600px"
      :before-close="handleChapterDialogClose"
    >
      <el-form :model="chapterForm" :rules="chapterRules" ref="chapterFormRef" label-width="100px">
        <el-form-item label="章节标题" prop="title">
          <el-input v-model="chapterForm.title" placeholder="请输入章节标题" />
        </el-form-item>
        
        <el-form-item label="章节摘要" prop="summary">
          <el-input 
            v-model="chapterForm.summary" 
            type="textarea" 
            :rows="3"
            placeholder="请输入章节摘要"
          />
        </el-form-item>
        
        <el-form-item label="详细内容" prop="content">
          <el-input 
            v-model="chapterForm.content" 
            type="textarea" 
            :rows="6"
            placeholder="请输入章节详细内容"
          />
        </el-form-item>
        
        <el-form-item label="关键概念">
          <el-input 
            v-model="conceptInput" 
            placeholder="输入概念后按回车添加"
            @keyup.enter="addConcept"
          />
          <div class="concepts-tags" style="margin-top: 8px;">
            <el-tag 
              v-for="(concept, index) in chapterForm.key_concepts" 
              :key="index"
              closable
              @close="removeConcept(index)"
              style="margin-right: 8px; margin-bottom: 4px;"
            >
              {{ concept }}
            </el-tag>
          </div>
        </el-form-item>
        
        <el-form-item label="预计时长" prop="estimated_minutes">
          <el-input-number 
            v-model="chapterForm.estimated_minutes" 
            :min="1" 
            :max="300"
            placeholder="分钟"
          />
        </el-form-item>
        
        <el-form-item label="章节顺序" prop="order">
          <el-input-number 
            v-model="chapterForm.order" 
            :min="1" 
            :max="100"
            placeholder="顺序"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleChapterDialogClose">取消</el-button>
        <el-button type="primary" @click="saveChapter" :loading="savingChapter">
          {{ editingChapter ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import MindMap from '@/components/MindMap.vue'
import CourseAnalytics from '@/components/CourseAnalytics.vue'
import api from '@/utils/api'

const router = useRouter()
const route = useRoute()
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
  mind_map_data?: any
  created_at: string
  updated_at: string
}

interface Chapter {
  id: string
  title: string
  summary: string
  content: string
  key_concepts: string[]
  order: number
  estimated_minutes: number
}

interface LearningProgress {
  id: string
  progress_percentage: number
  time_spent_minutes: number
  chapter_progress: Record<string, any>
  learning_notes: string
}

const course = ref<Course | null>(null)
const chapters = ref<Chapter[]>([])
const learningProgress = ref<LearningProgress | null>(null)
const loading = ref(true)
const showMindMap = ref(false)
const showChapterDetail = ref(false)
const selectedChapter = ref<Chapter | null>(null)
const showCreateChapterDialog = ref(false)
const editingChapter = ref<Chapter | null>(null)
const savingChapter = ref(false)
const conceptInput = ref('')
const generatingMindMap = ref(false)

// 章节表单
const chapterForm = reactive({
  title: '',
  summary: '',
  content: '',
  key_concepts: [] as string[],
  estimated_minutes: 30,
  order: 1
})

// 章节表单验证规则
const chapterRules = {
  title: [
    { required: true, message: '请输入章节标题', trigger: 'blur' }
  ],
  summary: [
    { required: true, message: '请输入章节摘要', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入章节内容', trigger: 'blur' }
  ],
  estimated_minutes: [
    { required: true, message: '请输入预计时长', trigger: 'blur' }
  ]
}

const courseId = route.params.id as string
const chapterFormRef = ref()

// 计算属性
const isInstructor = computed(() => {
  return course.value && authStore.user && course.value.instructor === authStore.user.id
})

const completedChaptersCount = computed(() => {
  if (!learningProgress.value?.chapter_progress) return 0
  return Object.keys(learningProgress.value.chapter_progress).length
})

onMounted(() => {
  loadCourseDetail()
})

const loadCourseDetail = async () => {
  try {
    loading.value = true
    
    // 加载课程信息
    const courseResponse = await api.get(`/learning/courses/${courseId}/`)
    course.value = courseResponse.data
    
    // 加载章节信息
    const chaptersResponse = await api.get(`/learning/courses/${courseId}/chapters/`)
    chapters.value = chaptersResponse.data
    
    // 加载学习进度
    try {
      const progressResponse = await api.get(`/learning/analytics/${courseId}/`)
      learningProgress.value = progressResponse.data
    } catch (error) {
      // 如果没有学习进度，忽略错误
      console.log('No learning progress found')
    }
    
  } catch (error) {
    ElMessage.error('加载课程详情失败')
  } finally {
    loading.value = false
  }
}

const viewChapter = (chapter: Chapter) => {
  selectedChapter.value = chapter
  showChapterDetail.value = true
}

const markChapterComplete = async () => {
  if (!selectedChapter.value) return
  
  try {
    await api.post(`/learning/courses/${courseId}/chapters/${selectedChapter.value.id}/progress/`, {
      completed: true,
      completed_at: new Date().toISOString()
    })
    
    ElMessage.success('章节标记为已完成')
    showChapterDetail.value = false
    loadCourseDetail() // 重新加载进度
  } catch (error) {
    ElMessage.error('标记失败')
  }
}

// 章节管理方法
const editChapter = (chapter: Chapter) => {
  editingChapter.value = chapter
  chapterForm.title = chapter.title
  chapterForm.summary = chapter.summary
  chapterForm.content = chapter.content
  chapterForm.key_concepts = [...chapter.key_concepts]
  chapterForm.estimated_minutes = chapter.estimated_minutes
  chapterForm.order = chapter.order
  showCreateChapterDialog.value = true
}

const deleteChapter = async (chapter: Chapter) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除章节"${chapter.title}"吗？此操作不可恢复！`, 
      '确认删除', 
      {
        type: 'error',
        confirmButtonText: '删除',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await api.delete(`/learning/chapters/${chapter.id}/`)
    ElMessage.success('章节删除成功')
    loadCourseDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addConcept = () => {
  if (conceptInput.value.trim()) {
    chapterForm.key_concepts.push(conceptInput.value.trim())
    conceptInput.value = ''
  }
}

const removeConcept = (index: number) => {
  chapterForm.key_concepts.splice(index, 1)
}

const saveChapter = async () => {
  if (!chapterFormRef.value) return
  
  await chapterFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      savingChapter.value = true
      try {
        if (editingChapter.value) {
          // 更新章节
          await api.put(`/learning/chapters/${editingChapter.value.id}/`, chapterForm)
          ElMessage.success('章节更新成功')
        } else {
          // 创建章节
          await api.post(`/learning/courses/${courseId}/chapters/`, chapterForm)
          ElMessage.success('章节创建成功')
        }
        
        handleChapterDialogClose()
        loadCourseDetail()
      } catch (error) {
        ElMessage.error(editingChapter.value ? '更新失败' : '创建失败')
      } finally {
        savingChapter.value = false
      }
    }
  })
}

const handleChapterDialogClose = () => {
  showCreateChapterDialog.value = false
  editingChapter.value = null
  // 重置表单
  chapterForm.title = ''
  chapterForm.summary = ''
  chapterForm.content = ''
  chapterForm.key_concepts = []
  chapterForm.estimated_minutes = 30
  chapterForm.order = 1
  conceptInput.value = ''
}


const publishCourse = async () => {
  if (!course.value) return
  
  try {
    await ElMessageBox.confirm('确定要发布这门课程吗？', '确认发布', {
      type: 'warning'
    })
    
    await api.post(`/learning/courses/${course.value.id}/publish/`)
    ElMessage.success('课程发布成功')
    loadCourseDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败')
    }
  }
}

const deleteCourse = async () => {
  if (!course.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${course.value.title}"吗？此操作不可恢复！`, 
      '确认删除', 
      {
        type: 'error',
        confirmButtonText: '删除',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await api.delete(`/learning/courses/${course.value.id}/delete/`)
    ElMessage.success('课程删除成功')
    router.push('/my-courses')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const generateMindMap = async () => {
  if (!course.value) return
  
  generatingMindMap.value = true
  try {
    const response = await api.get(`/learning/courses/${course.value.id}/mind-map/`)
    course.value.mind_map_data = response.data
    ElMessage.success('思维导图生成成功')
  } catch (error) {
    ElMessage.error('生成思维导图失败')
  } finally {
    generatingMindMap.value = false
  }
}

const handleMindMapClose = () => {
  showMindMap.value = false
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

const goBack = () => {
  router.push('/courses')
}
</script>

<style scoped>
.course-detail-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.course-header {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  color: #2c3e50;
  margin: 0;
}

.course-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.loading-container {
  padding: 20px;
}

.course-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.course-info-card {
  margin-bottom: 20px;
}

.course-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.course-basic {
  flex: 1;
}

.course-basic h3 {
  color: #2c3e50;
  margin: 0 0 12px 0;
}

.course-description {
  color: #7f8c8d;
  margin-bottom: 16px;
  line-height: 1.6;
}

.course-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.course-instructor,
.course-hours {
  color: #999;
  font-size: 14px;
}

.mind-map-section {
  margin-left: 20px;
}

.chapters-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-count {
  color: #999;
  font-size: 14px;
}

.empty-chapters {
  text-align: center;
  padding: 40px;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.chapter-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.chapter-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chapter-actions .delete-btn {
  color: #f56c6c;
}

.chapter-actions .delete-btn:hover {
  color: #f56c6c;
  background-color: #fef0f0;
}

.chapter-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
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

.chapter-info {
  flex: 1;
}

.chapter-info h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.chapter-summary {
  color: #7f8c8d;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.chapter-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.chapter-duration {
  color: #999;
  font-size: 14px;
}

.key-concepts {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.progress-card {
  margin-bottom: 20px;
}

.progress-content {
  padding: 16px 0;
}

.progress-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  color: #2c3e50;
  font-weight: bold;
}

.mind-map-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.mind-map-dialog .el-dialog__body) {
  padding: 0;
}

:deep(.mind-map-dialog .el-dialog) {
  max-height: 90vh;
}

.chapter-detail {
  max-height: 600px;
  overflow-y: auto;
}

.chapter-content h4 {
  color: #2c3e50;
  margin: 20px 0 12px 0;
}

.chapter-content h4:first-child {
  margin-top: 0;
}

.content-text {
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.concepts-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.concept-tag {
  margin: 4px 0;
}

.chapter-actions {
  margin-top: 20px;
  text-align: right;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}
</style>
