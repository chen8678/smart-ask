<!-- 思维导图测试页面 -->
<template>
  <div class="mindmap-test-container">
    <h2>思维导图功能测试</h2>
    
    <div class="test-section">
      <h3>测试知识库</h3>
      <p>知识库ID: {{ testKnowledgeBaseId }}</p>
      <p>知识库标题: {{ knowledgeBaseTitle }}</p>
    </div>

    <div class="test-section">
      <h3>API测试</h3>
      <div class="button-group">
        <el-button @click="testGenerateMindmap" :loading="loading.generate">
          生成思维导图
        </el-button>
        <el-button @click="testGetSummary" :loading="loading.summary">
          获取摘要
        </el-button>
        <el-button @click="testRefreshMindmap" :loading="loading.refresh">
          刷新思维导图
        </el-button>
      </div>
    </div>

    <div class="test-section" v-if="mindmapData">
      <h3>思维导图数据</h3>
      <el-card>
        <pre>{{ JSON.stringify(mindmapData, null, 2) }}</pre>
      </el-card>
    </div>

    <div class="test-section" v-if="summaryData">
      <h3>摘要数据</h3>
      <el-card>
        <pre>{{ JSON.stringify(summaryData, null, 2) }}</pre>
      </el-card>
    </div>

    <div class="test-section" v-if="mindmapData">
      <h3>思维导图可视化</h3>
      <MindMapVisualization 
        :knowledge-base-id="testKnowledgeBaseId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import MindMapVisualization from '@/components/MindMapVisualization.vue'
import api from '@/utils/api'

// 测试数据
const testKnowledgeBaseId = '117139b4-f1fa-4127-942f-eb71ccc61014'
const knowledgeBaseTitle = '法律知识库测试'

// 响应式数据
const loading = reactive({
  generate: false,
  summary: false,
  refresh: false
})

const mindmapData = ref(null)
const summaryData = ref(null)

// 测试生成思维导图
const testGenerateMindmap = async () => {
  loading.generate = true
  try {
    const response = await api.get(`/learning/mindmap/${testKnowledgeBaseId}/`)
    mindmapData.value = response.data
    ElMessage.success('思维导图生成成功')
  } catch (error) {
    console.error('生成思维导图失败:', error)
    ElMessage.error('生成思维导图失败')
  } finally {
    loading.generate = false
  }
}

// 测试获取摘要
const testGetSummary = async () => {
  loading.summary = true
  try {
    const response = await api.get(`/learning/mindmap/${testKnowledgeBaseId}/summary/`)
    summaryData.value = response.data
    ElMessage.success('摘要获取成功')
  } catch (error) {
    console.error('获取摘要失败:', error)
    ElMessage.error('获取摘要失败')
  } finally {
    loading.summary = false
  }
}

// 测试刷新思维导图
const testRefreshMindmap = async () => {
  loading.refresh = true
  try {
    const response = await api.post(`/learning/mindmap/${testKnowledgeBaseId}/refresh/`)
    mindmapData.value = response.data
    ElMessage.success('思维导图刷新成功')
  } catch (error) {
    console.error('刷新思维导图失败:', error)
    ElMessage.error('刷新思维导图失败')
  } finally {
    loading.refresh = false
  }
}
</script>

<style scoped>
.mindmap-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

pre {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.4;
}
</style>
