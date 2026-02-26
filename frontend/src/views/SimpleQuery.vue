<template>
  <div class="simple-query-container">
    <div class="query-header">
      <h2>FastGPT 智能体资料库查询</h2>
      <p class="subtitle">私有知识库，专业准确</p>
    </div>

    <div class="query-form">
      <el-input
        v-model="question"
        type="textarea"
        :rows="3"
        placeholder="请输入您的问题，例如：BIM里规划的塔吊安全距离是多少？"
        @keyup.enter.ctrl="handleQuery"
      />
      
      <div class="query-actions">
        <el-button 
          type="primary" 
          @click="handleQuery"
          :loading="loading"
          :disabled="!question.trim()"
        >
          查询
        </el-button>
        <el-button @click="clearQuery">清空</el-button>
      </div>
    </div>

    <div v-if="result" class="query-result">
      <div class="result-header">
        <el-tag type="success" size="small">私有知识库</el-tag>
        <span class="result-label">专业准确</span>
      </div>
      
      <div class="answer-section">
        <h3>答案：</h3>
        <div class="answer-content" v-html="formatAnswer(result.answer)"></div>
      </div>
      
      <div v-if="result.sources && result.sources.length > 0" class="sources-section">
        <h3>参考来源：</h3>
        <ul class="sources-list">
          <li v-for="(source, index) in result.sources" :key="index">
            {{ source }}
          </li>
        </ul>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <el-alert
        :title="error"
        type="error"
        :closable="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const question = ref('')
const loading = ref(false)
const result = ref<any>(null)
const error = ref('')

const handleQuery = async () => {
  if (!question.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  loading.value = true
  error.value = ''
  result.value = null

  try {
    const response = await api.post('/api/v1/chat/simple-query/', {
      question: question.value
    })
    
    result.value = response.data
    ElMessage.success('查询成功')
  } catch (err: any) {
    error.value = err.response?.data?.error || '查询失败，请稍后重试'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const clearQuery = () => {
  question.value = ''
  result.value = null
  error.value = ''
}

const formatAnswer = (answer: string) => {
  // 简单的格式化：将换行转换为<br>
  return answer.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.simple-query-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.query-header {
  text-align: center;
  margin-bottom: 30px;
}

.query-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.query-form {
  margin-bottom: 30px;
}

.query-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.query-result {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.result-label {
  color: #67c23a;
  font-size: 14px;
  font-weight: 500;
}

.answer-section {
  margin-bottom: 20px;
}

.answer-section h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.answer-content {
  background: white;
  padding: 15px;
  border-radius: 4px;
  line-height: 1.6;
  color: #606266;
}

.sources-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
}

.sources-section h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.sources-list {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.sources-list li {
  margin-bottom: 5px;
}

.error-message {
  margin-top: 20px;
}
</style>

