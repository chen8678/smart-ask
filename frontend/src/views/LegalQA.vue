<!-- 法律问答界面 -->
<template>
  <div class="legal-qa-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>法律智能问答</h1>
      <p>基于RAG技术的专业法律问答服务</p>
    </div>

    <!-- 查询输入区域 -->
    <div class="query-section">
      <el-card class="query-card">
        <template #header>
          <div class="card-header">
            <span>法律问题查询</span>
            <el-tag type="info">支持脱敏处理</el-tag>
          </div>
        </template>
        
        <el-form :model="queryForm" label-width="100px">
          <el-form-item label="问题类型">
            <el-select v-model="queryForm.query_type" placeholder="请选择问题类型">
              <el-option label="法律问题" value="question"></el-option>
              <el-option label="案例分析" value="case_analysis"></el-option>
              <el-option label="合同审查" value="contract_review"></el-option>
              <el-option label="法律研究" value="legal_research"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="法律问题">
            <el-input
              v-model="queryForm.query"
              type="textarea"
              :rows="4"
              placeholder="请输入您的法律问题..."
              maxlength="1000"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="上下文">
            <el-input
              v-model="queryForm.context"
              type="textarea"
              :rows="3"
              placeholder="可选：提供相关背景信息..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="知识库">
            <el-select v-model="queryForm.knowledge_base_id" placeholder="选择知识库（可选）">
              <el-option
                v-for="kb in knowledgeBases"
                :key="kb.id"
                :label="kb.name"
                :value="kb.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
        
        <!-- 脱敏选项 -->
        <div class="desensitization-options">
          <el-divider content-position="left">脱敏选项</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-checkbox v-model="queryForm.enable_desensitization">
                启用数据脱敏
              </el-checkbox>
              <el-tooltip content="自动检测并脱敏敏感信息" placement="top">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-col>
            <el-col :span="12">
              <el-checkbox v-model="queryForm.restore_result" :disabled="!queryForm.enable_desensitization">
                恢复脱敏结果
              </el-checkbox>
              <el-tooltip content="在答案中恢复敏感信息（需要权限）" placement="top">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-col>
          </el-row>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="primary" @click="submitQuery" :loading="loading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="clearForm">
            <el-icon><Refresh /></el-icon>
            清空
          </el-button>
          <el-button @click="showHistory">
            <el-icon><Clock /></el-icon>
            查询历史
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 结果显示区域 -->
    <div class="results-section" v-if="queryResult">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <span>查询结果</span>
            <div class="result-meta">
              <el-tag :type="getConfidenceType(queryResult.confidence_score)">
                置信度: {{ (queryResult.confidence_score * 100).toFixed(1) }}%
              </el-tag>
              <el-tag type="info">
                处理时间: {{ queryResult.processing_time?.toFixed(2) }}s
              </el-tag>
            </div>
          </div>
        </template>
        
        <!-- 答案内容 -->
        <div class="answer-content">
          <h3>法律建议</h3>
          <div class="answer-text" v-html="formatAnswer(queryResult.answer)"></div>
        </div>
        
        <!-- 脱敏信息 -->
        <div class="desensitization-info" v-if="queryResult.desensitization_info">
          <el-divider content-position="left">脱敏信息</el-divider>
          <el-alert
            :title="getDesensitizationMessage(queryResult.desensitization_info)"
            :type="queryResult.desensitization_info.enabled ? 'success' : 'info'"
            :closable="false"
            show-icon
          />
        </div>
        
        <!-- 相关文档 -->
        <div class="relevant-documents" v-if="queryResult.relevant_documents?.length">
          <el-divider content-position="left">相关法律条文</el-divider>
          <el-timeline>
            <el-timeline-item
              v-for="(doc, index) in queryResult.relevant_documents"
              :key="index"
              :timestamp="`相似度: ${(doc.similarity * 100).toFixed(1)}%`"
            >
              <el-card>
                <h4>{{ doc.title }}</h4>
                <p>{{ doc.preview }}</p>
                <el-tag size="small">{{ getDocumentTypeName(doc.type) }}</el-tag>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
        
        <!-- 相关案例 -->
        <div class="relevant-cases" v-if="queryResult.relevant_cases?.length">
          <el-divider content-position="left">相关案例</el-divider>
          <el-timeline>
            <el-timeline-item
              v-for="(case, index) in queryResult.relevant_cases"
              :key="index"
              :timestamp="`相似度: ${(case.similarity * 100).toFixed(1)}%`"
            >
              <el-card>
                <h4>{{ case.title }}</h4>
                <p>{{ case.preview }}</p>
                <el-tag size="small">{{ getCaseTypeName(case.type) }}</el-tag>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
    </div>

    <!-- 查询历史对话框 -->
    <el-dialog v-model="historyDialogVisible" title="查询历史" width="80%">
      <el-table :data="queryHistory" style="width: 100%">
        <el-table-column prop="query_type" label="类型" width="120">
          <template #default="scope">
            <el-tag size="small">{{ getQueryTypeName(scope.row.query_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question" label="问题" min-width="200" />
        <el-table-column prop="answer" label="答案" min-width="200" />
        <el-table-column prop="confidence_score" label="置信度" width="100">
          <template #default="scope">
            {{ (scope.row.confidence_score * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="viewHistoryDetail(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-pagination
          v-model:current-page="historyPage"
          :page-size="historyPageSize"
          :total="historyTotal"
          @current-change="loadQueryHistory"
          layout="total, prev, pager, next"
        />
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Clock, QuestionFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const historyDialogVisible = ref(false)
const queryResult = ref(null)
const knowledgeBases = ref([])
const queryHistory = ref([])
const historyPage = ref(1)
const historyPageSize = ref(20)
const historyTotal = ref(0)

// 查询表单
const queryForm = reactive({
  query: '',
  context: '',
  query_type: 'question',
  knowledge_base_id: '',
  enable_desensitization: true,
  restore_result: false
})

// 页面加载时获取知识库列表
onMounted(() => {
  loadKnowledgeBases()
})

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const response = await api.get('/legal/knowledge-bases/')
    knowledgeBases.value = response.data.knowledge_bases || []
  } catch (error) {
    console.error('加载知识库失败:', error)
  }
}

// 提交查询
const submitQuery = async () => {
  if (!queryForm.query.trim()) {
    ElMessage.warning('请输入法律问题')
    return
  }

  loading.value = true
  try {
    const response = await api.post('/integration/legal-qa/', queryForm)
    queryResult.value = response.data
    
    ElMessage.success('查询成功')
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 清空表单
const clearForm = () => {
  queryForm.query = ''
  queryForm.context = ''
  queryForm.knowledge_base_id = ''
  queryForm.enable_desensitization = true
  queryForm.restore_result = false
  queryResult.value = null
}

// 显示查询历史
const showHistory = () => {
  historyDialogVisible.value = true
  loadQueryHistory()
}

// 加载查询历史
const loadQueryHistory = async () => {
  try {
    const response = await api.get('/integration/legal-query-history/', {
      params: {
        page: historyPage.value,
        page_size: historyPageSize.value
      }
    })
    queryHistory.value = response.data.queries || []
    historyTotal.value = response.data.total || 0
  } catch (error) {
    console.error('加载查询历史失败:', error)
  }
}

// 查看历史详情
const viewHistoryDetail = (row: any) => {
  ElMessageBox.alert(row.answer, `问题: ${row.question}`, {
    confirmButtonText: '确定',
    dangerouslyUseHTMLString: true
  })
}

// 格式化答案
const formatAnswer = (answer: string) => {
  if (!answer) return ''
  return answer.replace(/\n/g, '<br>')
}

// 获取置信度类型
const getConfidenceType = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'danger'
}

// 获取脱敏信息消息
const getDesensitizationMessage = (info: any) => {
  if (!info.enabled) return '未启用数据脱敏'
  if (info.sensitive_items_detected > 0) {
    return `已检测到 ${info.sensitive_items_detected} 项敏感信息并脱敏处理`
  }
  return '未检测到敏感信息'
}

// 获取文档类型名称
const getDocumentTypeName = (type: string) => {
  const typeMap = {
    'law': '法律条文',
    'regulation': '行政法规',
    'case': '案例',
    'contract': '合同',
    'opinion': '法律意见',
    'precedent': '判例',
    'other': '其他'
  }
  return typeMap[type] || type
}

// 获取案例类型名称
const getCaseTypeName = (type: string) => {
  const typeMap = {
    'civil': '民事案例',
    'criminal': '刑事案例',
    'administrative': '行政案例',
    'commercial': '商事案例',
    'labor': '劳动争议案例',
    'other': '其他'
  }
  return typeMap[type] || type
}

// 获取查询类型名称
const getQueryTypeName = (type: string) => {
  const typeMap = {
    'question': '法律问题',
    'case_analysis': '案例分析',
    'contract_review': '合同审查',
    'legal_research': '法律研究',
    'other': '其他'
  }
  return typeMap[type] || type
}
</script>

<style scoped>
.legal-qa-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.query-section {
  margin-bottom: 30px;
}

.query-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.desensitization-options {
  margin: 20px 0;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
}

.action-buttons .el-button {
  margin: 0 10px;
}

.results-section {
  margin-bottom: 30px;
}

.result-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.result-meta {
  display: flex;
  gap: 10px;
}

.answer-content {
  margin-bottom: 20px;
}

.answer-content h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.answer-text {
  line-height: 1.6;
  color: #34495e;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.desensitization-info {
  margin: 20px 0;
}

.relevant-documents,
.relevant-cases {
  margin-top: 20px;
}

.relevant-documents .el-card,
.relevant-cases .el-card {
  margin-bottom: 10px;
}

.relevant-documents h4,
.relevant-cases h4 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.relevant-documents p,
.relevant-cases p {
  color: #7f8c8d;
  margin-bottom: 10px;
}
</style>
