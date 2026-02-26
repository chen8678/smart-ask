<!-- 知识库思维导图组件 -->
<template>
  <div class="mindmap-container">
    <!-- 顶部工具栏 -->
    <div class="mindmap-toolbar">
      <div class="toolbar-left">
        <h3>{{ knowledgeBaseTitle }}</h3>
        <el-tag type="info" v-if="summary">
          节点: {{ summary.total_nodes }} | 分支: {{ summary.total_branches }} | 关系: {{ summary.total_relationships }}
        </el-tag>
      </div>
      <div class="toolbar-right">
        <el-button @click="refreshMindmap" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportMindmap" :disabled="!mindmapData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
        <el-button @click="toggleFullscreen">
          <el-icon><FullScreen /></el-icon>
          {{ isFullscreen ? '退出全屏' : '全屏' }}
        </el-button>
      </div>
    </div>

    <!-- 思维导图内容 -->
    <div class="mindmap-content" :class="{ 'fullscreen': isFullscreen }">
      <div v-if="loading" class="loading-container">
        <el-loading-spinner />
        <p>正在生成思维导图...</p>
      </div>

      <div v-else-if="error" class="error-container">
        <el-alert
          :title="error"
          type="error"
          :closable="false"
          show-icon
        />
        <el-button @click="loadMindmap" style="margin-top: 20px;">
          重新加载
        </el-button>
      </div>

      <div v-else-if="mindmapData" class="mindmap-visualization">
        <!-- 使用简单的HTML/CSS实现思维导图 -->
        <div class="mindmap-tree">
          <MindMapNode 
            :node="mindmapData" 
            :level="0"
            @node-click="handleNodeClick"
          />
        </div>
      </div>

      <div v-else class="empty-container">
        <el-empty description="暂无思维导图数据">
          <el-button type="primary" @click="loadMindmap">
            生成思维导图
          </el-button>
        </el-empty>
      </div>
    </div>

    <!-- 节点详情侧边栏 -->
    <el-drawer
      v-model="drawerVisible"
      title="节点详情"
      :size="400"
      direction="rtl"
    >
      <div v-if="selectedNode" class="node-details">
        <h4>{{ selectedNode.text }}</h4>
        <el-divider />
        
        <div class="node-info">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="类型">
              <el-tag :type="getNodeTypeColor(selectedNode.type)">
                {{ getNodeTypeName(selectedNode.type) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="重要性" v-if="selectedNode.importance">
              {{ selectedNode.importance }}%
            </el-descriptions-item>
            <el-descriptions-item label="频率" v-if="selectedNode.frequency">
              {{ selectedNode.frequency }}
            </el-descriptions-item>
            <el-descriptions-item label="权重" v-if="selectedNode.weight">
              {{ selectedNode.weight }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="selectedNode.children && selectedNode.children.length" class="node-children">
          <h5>子节点</h5>
          <el-tag 
            v-for="child in selectedNode.children" 
            :key="child.id"
            style="margin: 2px;"
            @click="handleNodeClick(child)"
          >
            {{ child.text }}
          </el-tag>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, FullScreen } from '@element-plus/icons-vue'
import api from '@/utils/api'

// Props
const props = defineProps<{
  knowledgeBaseId: string
}>()

// 响应式数据
const loading = ref(false)
const refreshing = ref(false)
const error = ref('')
const mindmapData = ref(null)
const summary = ref(null)
const drawerVisible = ref(false)
const selectedNode = ref(null)
const isFullscreen = ref(false)

// 计算属性
const knowledgeBaseTitle = computed(() => {
  return mindmapData.value?.knowledge_base_title || '知识库思维导图'
})

// 组件挂载时加载思维导图
onMounted(() => {
  loadMindmap()
})

// 加载思维导图
const loadMindmap = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await api.get(`/learning/mindmap/${props.knowledgeBaseId}/`)
    mindmapData.value = response.data.mindmap
    knowledgeBaseTitle.value = response.data.knowledge_base_title
    
    // 同时加载摘要
    await loadSummary()
    
    ElMessage.success('思维导图加载成功')
  } catch (err) {
    console.error('加载思维导图失败:', err)
    error.value = err.response?.data?.error || '加载思维导图失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 加载摘要
const loadSummary = async () => {
  try {
    const response = await api.get(`/learning/mindmap/${props.knowledgeBaseId}/summary/`)
    summary.value = response.data.summary
  } catch (err) {
    console.error('加载摘要失败:', err)
  }
}

// 刷新思维导图
const refreshMindmap = async () => {
  refreshing.value = true
  
  try {
    const response = await api.post(`/learning/mindmap/${props.knowledgeBaseId}/refresh/`)
    mindmapData.value = response.data.mindmap
    await loadSummary()
    
    ElMessage.success('思维导图已刷新')
  } catch (err) {
    console.error('刷新思维导图失败:', err)
    ElMessage.error('刷新思维导图失败')
  } finally {
    refreshing.value = false
  }
}

// 导出思维导图
const exportMindmap = () => {
  if (!mindmapData.value) return
  
  // 简单的导出功能（可以后续扩展为更复杂的导出）
  const data = {
    title: knowledgeBaseTitle.value,
    mindmap: mindmapData.value,
    summary: summary.value,
    exported_at: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${knowledgeBaseTitle.value}_思维导图.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('思维导图已导出')
}

// 切换全屏
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

// 处理节点点击
const handleNodeClick = (node: any) => {
  selectedNode.value = node
  drawerVisible.value = true
}

// 获取节点类型颜色
const getNodeTypeColor = (type: string) => {
  const colorMap = {
    'root': 'primary',
    'branch': 'success',
    'topic': 'warning',
    'concept': 'info',
    'keyword': 'default',
    'empty': 'info',
    'error': 'danger'
  }
  return colorMap[type] || 'default'
}

// 获取节点类型名称
const getNodeTypeName = (type: string) => {
  const nameMap = {
    'root': '根节点',
    'branch': '分支',
    'topic': '主题',
    'concept': '概念',
    'keyword': '关键词',
    'empty': '空节点',
    'error': '错误节点'
  }
  return nameMap[type] || type
}
</script>

<style scoped>
.mindmap-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mindmap-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-left h3 {
  margin: 0;
  color: #303133;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.mindmap-content {
  flex: 1;
  padding: 20px;
  background: #f5f7fa;
  overflow: auto;
}

.mindmap-content.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: #fff;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.mindmap-visualization {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.mindmap-tree {
  min-height: 400px;
}

.node-details {
  padding: 20px;
}

.node-info {
  margin-bottom: 20px;
}

.node-children h5 {
  margin-bottom: 10px;
  color: #606266;
}

.node-children .el-tag {
  cursor: pointer;
}
</style>
