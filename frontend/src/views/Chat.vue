<template>
  <div class="chat-container">
    <!-- 顶部导航 -->
    <div class="chat-header">
      <div class="header-content">
        <div class="header-left">
          <div class="header-title">
            <div class="title-icon">
              <AppleIcon name="cube" :size="22" />
            </div>
            <div class="title-text">
              <h2>BIM · 智慧工地对话</h2>
              <p>基于 BIM 知识库与标准答案的现场问答助手</p>
            </div>
          </div>
        </div>
        
        <div class="header-controls">
          <div class="control-card">
            <div class="control-group">
              <label>知识库</label>
              <el-select
                v-model="selectedKnowledgeBase"
                placeholder="选择知识库"
                class="control-select"
                @change="onKnowledgeBaseChange"
                size="small"
              >
                <el-option
                  v-for="kb in knowledgeBases"
                  :key="kb.id"
                  :label="kb.title"
                  :value="kb.id"
                />
              </el-select>
            </div>
            
            <div class="control-group">
              <label>AI提供商</label>
              <el-select
                v-model="selectedProvider"
                placeholder="选择AI提供商"
                class="control-select"
                @change="onProviderChange"
                size="small"
              >
                <el-option
                  v-for="provider in configuredProviders"
                  :key="provider.key"
                  :label="provider.name"
                  :value="provider.key"
                >
                  <span>
                    {{ provider.name }}
                    <el-tag size="small" :type="provider.available ? 'success' : 'danger'" style="margin-left: 8px;">
                      {{ provider.available ? '已配置' : '未配置' }}
                    </el-tag>
                  </span>
                </el-option>
              </el-select>
            </div>
            
            <div class="control-group">
              <label>模型</label>
              <el-select
                v-model="selectedModel"
                placeholder="选择具体模型"
                class="control-select"
                @change="onModelChange"
                :disabled="!selectedProvider"
                size="small"
              >
                <el-option
                  v-for="model in availableModels"
                  :key="model.key"
                  :label="model.name"
                  :value="model.key"
                >
                  <span>
                    {{ model.name }}
                    <el-tag size="small" type="info" style="margin-left: 8px;">
                      {{ model.version }}
                    </el-tag>
                  </span>
                </el-option>
              </el-select>
            </div>
          </div>
        </div>
        
        <div class="header-actions">
          <el-button @click="goToConfig" type="warning" size="small" round>
            <AppleIcon name="settings" :size="16" />
            AI配置
          </el-button>
          <el-button @click="showStrategyPanel = true" type="success" size="small" round>
            策略/证据面板
          </el-button>
          <el-button @click="showSessionList = true" type="primary" size="small" round>
            <AppleIcon name="chat-bubble" :size="16" />
            会话列表
          </el-button>
          <el-button @click="goBack" type="info" size="small" round>
            <AppleIcon name="arrow-left" :size="16" />
            返回
          </el-button>
        </div>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-main">
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-chat">
          <div class="empty-icon">
            <el-icon size="48"><ChatDotRound /></el-icon>
          </div>
          <h3>开始对话</h3>
          <p>选择一个知识库和AI模型，开始您的智能问答之旅</p>
        </div>
        
        <div
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="{ 
            'user-message': message.role === 'user', 
            'ai-message': message.role === 'assistant',
            'error-message': message.isError
          }"
        >
          <div class="message-avatar">
            <AppleIcon v-if="message.role === 'user'" name="user" :size="18" />
            <AppleIcon v-else-if="message.isError" name="warning" :size="18" />
            <AppleIcon v-else name="chat-bubble" :size="18" />
          </div>
          <div class="message-content">
            <div v-if="message.role === 'user'" class="message-text user-message">
              {{ message.content }}
            </div>
            <div v-else-if="message.isError" class="message-text error-text" v-html="formatMessage(message.content)"></div>
            <div v-else class="ai-answer-container">
              <AnswerDisplay 
                :content="message.content" 
                :sources="message.sources" 
                :timestamp="message.timestamp"
              />
            </div>
            <div class="message-meta">
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              <span v-if="message.tokens_used" class="message-tokens">
                <AppleIcon name="cpu" :size="12" />
                {{ message.tokens_used }} tokens
              </span>
              <span v-if="message.isError" class="error-tag">
                <AppleIcon name="warning" :size="12" />
                {{ message.errorType === 'warning' ? '警告' : '错误' }}
              </span>
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="message ai-message">
          <div class="message-avatar">
            <AppleIcon name="chat-bubble" :size="18" />
          </div>
          <div class="message-content">
            <div class="loading-indicator">
              <div class="loading-content">
                <AppleIcon class="is-loading" name="loading" :size="18" :spin="true" />
                <span>AI正在思考中...</span>
              </div>
              <el-button 
                @click="stopGeneration" 
                type="danger" 
                size="small" 
                class="stop-button"
              >
                <AppleIcon name="stop" :size="14" />
                停止生成
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-footer">
      <div class="input-container">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            placeholder="请输入您的问题..."
            @keyup.enter="sendMessage"
            :disabled="!selectedKnowledgeBase || loading"
            size="large"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            resize="none"
            class="message-input"
          />
          <div class="input-actions">
              <el-button
              @click="sendMessage"
              type="primary"
              :disabled="!inputMessage || !selectedKnowledgeBase || loading"
              :loading="loading"
              size="large"
              round
            >
              <template v-if="!loading">
                <AppleIcon name="arrow-right" :size="16" />
                发送
              </template>
              <template v-else>发送中...</template>
            </el-button>
          </div>
        </div>
        <div class="input-tips">
          <span v-if="!selectedKnowledgeBase" class="tip-warning">
            <AppleIcon name="warning" :size="14" />
            请先选择知识库
          </span>
          <span v-else class="tip-info">
            <AppleIcon name="info" :size="14" />
            按 Enter 发送，Shift + Enter 换行
          </span>
        </div>
      </div>
    </div>

    <!-- 会话列表对话框 -->
    <el-dialog
      v-model="showSessionList"
      title="会话列表"
      width="700px"
      :before-close="handleSessionListClose"
      class="session-dialog"
    >
      <div class="session-list">
        <div class="session-item" 
             v-for="session in sessions" 
             :key="session.id"
             @click="loadSession(session.id)"
             :class="{ 'active': currentSessionId === session.id }"
        >
          <div class="session-avatar">
            <AppleIcon name="chat-bubble" :size="18" />
          </div>
          <div class="session-info">
            <div class="session-title">{{ session.title || '未命名对话' }}</div>
            <div class="session-meta">
            <span class="session-time">
              <AppleIcon name="clock" :size="12" />
                {{ formatTime(session.updated_at) }}
              </span>
              <span class="session-count">
                <AppleIcon name="message" :size="12" />
                {{ session.message_count || 0 }} 条消息
              </span>
            </div>
            <div v-if="session.last_message" class="last-message">
              {{ session.last_message }}
            </div>
          </div>
          <div class="session-actions">
            <el-button
              @click.stop="deleteSession(session.id)"
              type="danger"
              size="small"
              circle
            >
              <AppleIcon name="trash" :size="12" />
            </el-button>
          </div>
        </div>
        <div v-if="sessions.length === 0" class="empty-sessions">
          <div class="empty-icon">
            <el-icon size="48"><ChatDotRound /></el-icon>
          </div>
          <h3>暂无会话记录</h3>
          <p>开始新的对话，创建您的第一个会话</p>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showSessionList = false" size="large">
            <AppleIcon name="stop" :size="14" />
            关闭
          </el-button>
          <el-button @click="createNewSession" type="primary" size="large">
            <AppleIcon name="plus" :size="14" />
            新建对话
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 策略/证据面板 -->
    <el-drawer v-model="showStrategyPanel" title="检索策略与证据" size="420px" direction="rtl">
      <div class="strategy-form">
        <el-form label-width="110px">
          <el-form-item label="检索策略">
            <el-select v-model="strategy.strategy" placeholder="选择检索策略" @change="onStrategyChange">
              <el-option
                v-for="(config, key) in retrievalStrategies"
                :key="key"
                :label="config.name"
                :value="key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Top K">
            <el-input-number v-model="strategy.top_k" :min="1" :max="20" />
          </el-form-item>
          <el-form-item label="阈值">
            <el-slider v-model="strategy.score_threshold" :min="0" :max="1" :step="0.01" show-input />
          </el-form-item>
          <el-form-item label="融合权重α" v-if="strategy.strategy === 'hybrid'">
            <el-slider v-model="strategy.alpha" :min="0" :max="1" :step="0.05" show-input />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!selectedKnowledgeBase || previewLoading" @click="previewRetrieval">
              {{ previewLoading ? '预览中...' : '预览证据' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="evidence-list" v-if="evidence.length">
        <h4>证据（{{ evidence.length }}）</h4>
        <div class="evidence-stats" v-if="retrievalStats">
          <el-tag size="small" type="success">总计: {{ retrievalStats.total_found }}</el-tag>
          <el-tag size="small" type="primary">去重: {{ retrievalStats.unique_found }}</el-tag>
        </div>
        <el-timeline>
          <el-timeline-item
            v-for="(ev, idx) in evidence"
            :key="idx"
            :timestamp="'Rank ' + ev.rank"
            type="primary"
          >
            <div class="evidence-item">
              <div class="evidence-title">{{ ev.source.title }}</div>
              <div class="evidence-meta">
                <el-tag size="small" type="success">Score: {{ ev.score }}</el-tag>
                <el-tag size="small" type="info" v-if="ev.vector_score !== undefined">V: {{ ev.vector_score }}</el-tag>
                <el-tag size="small" type="warning" v-if="ev.bm25_score !== undefined">B: {{ ev.bm25_score }}</el-tag>
                <el-tag size="small" type="info">KB: {{ ev.source.knowledge_base_id.slice(0,8) }}</el-tag>
                <el-tag size="small" :type="ev.dedupe_reason === 'unique' ? 'success' : 'warning'">{{ ev.dedupe_reason }}</el-tag>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
      <el-empty v-else description="暂无证据，调整策略后重试" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import AnswerDisplay from '@/components/AnswerDisplay.vue'
import AppleIcon from '@/components/AppleIcon.vue'

const router = useRouter()

// 响应式数据
const selectedKnowledgeBase = ref<string>('')
const selectedProvider = ref<string>('')
const selectedModel = ref<string>('')
const knowledgeBases = ref<any[]>([])
const configuredProviders = ref<any[]>([])
const availableModels = ref<any[]>([])
const messages = ref<any[]>([])
const inputMessage = ref('')
const loading = ref(false)
const currentRequestController = ref<AbortController | null>(null)
const isGenerating = ref(false)
const showSessionList = ref(false)
const sessions = ref<any[]>([])
const currentSessionId = ref<string | null>(null)
const messagesContainer = ref<HTMLElement>()
const showStrategyPanel = ref(false)
const previewLoading = ref(false)
const retrievalStrategies = ref<any>({})
const retrievalStats = ref<any>(null)
const strategy = reactive({
  strategy: 'hybrid',
  top_k: 5,
  score_threshold: 0.2,
  alpha: 0.5
})
const evidence = ref<any[]>([])

// 加载检索策略
const loadRetrievalStrategies = async () => {
  try {
    const response = await api.get('/knowledge/retrieval-strategies/')
    retrievalStrategies.value = response.data.strategies
    strategy.strategy = response.data.default_strategy
  } catch (error) {
    console.error('加载检索策略失败:', error)
    ElMessage.error('加载检索策略失败')
  }
}

// 策略变更处理
const onStrategyChange = (strategyName: string) => {
  const config = retrievalStrategies.value[strategyName]
  if (config && config.default_params) {
    // 更新默认参数
    if (config.default_params.top_k !== undefined) {
      strategy.top_k = config.default_params.top_k
    }
    if (config.default_params.score_threshold !== undefined) {
      strategy.score_threshold = config.default_params.score_threshold
    }
    if (config.default_params.alpha !== undefined) {
      strategy.alpha = config.default_params.alpha
    }
  }
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const response = await api.get('/knowledge/knowledge-bases/')
    knowledgeBases.value = response.data
    if (knowledgeBases.value.length > 0) {
      selectedKnowledgeBase.value = knowledgeBases.value[0].id
    }
  } catch (error) {
    console.error('加载知识库失败:', error)
    ElMessage.error('加载知识库失败')
  }
}

// 加载AI配置
const loadAIConfig = async () => {
  try {
    console.log('开始加载AI配置...')
    const response = await api.get('/chat/providers/')
    console.log('AI配置API响应:', response.data)
    configuredProviders.value = response.data || []
    console.log('配置的提供商:', configuredProviders.value)
    
    if (configuredProviders.value.length > 0) {
      selectedProvider.value = configuredProviders.value[0].key
      loadAvailableModels()
    } else {
      console.warn('没有可用的AI提供商')
      // 设置默认值以防万一
      selectedProvider.value = 'deepseek'
      selectedModel.value = 'deepseek-chat'
    }
  } catch (error) {
    console.error('加载AI配置失败:', error)
    ElMessage.error('加载AI配置失败')
    // 设置默认值以防万一
    selectedProvider.value = 'deepseek'
    selectedModel.value = 'deepseek-chat'
  }
}

// 加载可用模型
const loadAvailableModels = () => {
  const provider = configuredProviders.value.find(p => p.key === selectedProvider.value)
  if (provider) {
    availableModels.value = provider.models || []
    if (availableModels.value.length > 0) {
      // 为了演示视频，写死使用第一个模型
      selectedModel.value = availableModels.value[0].key
      console.log('选择的模型:', selectedModel.value)
    }
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || !selectedKnowledgeBase.value || loading.value) {
    return
  }

  const userMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const question = inputMessage.value
  inputMessage.value = ''
  loading.value = true
  isGenerating.value = true

  // 创建AbortController用于取消请求
  const controller = new AbortController()
  currentRequestController.value = controller

  try {
    const requestData = {
      question,
      knowledge_base_id: selectedKnowledgeBase.value,
      model: selectedModel.value,
      strategy: strategy.strategy,
      top_k: strategy.top_k,
      score_threshold: strategy.score_threshold,
      alpha: strategy.alpha,
    }
    console.log('发送聊天请求:', requestData)
    console.log('当前选择的知识库:', selectedKnowledgeBase.value)
    console.log('当前选择的模型:', selectedModel.value)
    
    const response = await api.post('/chat/ask/', requestData, {
      signal: controller.signal
    })

    const aiMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: response.data.answer,
      timestamp: new Date(),
      tokens_used: response.data.tokens_used
    }

    messages.value.push(aiMessage)
  } catch (error) {
    console.error('发送消息失败:', error)
    
    // 检查是否是用户主动取消
    if (error.name === 'AbortError' || error.code === 'ERR_CANCELED') {
      console.log('用户取消了请求')
      ElMessage.info('已停止生成')
      return
    }
    
    // 解析错误信息
    let errorMessage = '发送消息失败，请重试'
    let errorType = 'error'
    
    if (error.response?.data?.error) {
      const errorData = error.response.data.error
      if (errorData.message?.includes('Authentication Fails') || errorData.message?.includes('invalid')) {
        errorMessage = 'API密钥无效，请检查AI模型配置'
        errorType = 'warning'
      } else if (errorData.message?.includes('rate limit')) {
        errorMessage = 'API调用频率过高，请稍后再试'
        errorType = 'warning'
      } else if (errorData.message) {
        errorMessage = `API错误: ${errorData.message}`
      }
    } else if (error.response?.status === 400) {
      errorMessage = '请求参数错误，请检查输入内容'
    } else if (error.response?.status === 401) {
      errorMessage = '身份验证失败，请重新登录'
    } else if (error.response?.status === 500) {
      errorMessage = '服务器内部错误，请稍后重试'
    }
    
    // 在聊天界面显示错误消息
    const errorMsg = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: errorMessage,
      timestamp: new Date(),
      isError: true,
      errorType: errorType
    }
    
    messages.value.push(errorMsg)
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
    isGenerating.value = false
    currentRequestController.value = null
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// 停止生成
const stopGeneration = () => {
  if (currentRequestController.value) {
    currentRequestController.value.abort()
    ElMessage.info('正在停止生成...')
  }
}

// 格式化消息内容
const formatMessage = (content: string) => {
  return content.replace(/\n/g, '<br>')
}

// 格式化时间
const formatTime = (timestamp: Date | string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 加载会话列表
const loadSessions = async () => {
  try {
    const response = await api.get('/chat/sessions/')
    sessions.value = response.data
  } catch (error) {
    console.error('加载会话列表失败:', error)
  }
}

// 加载会话
const loadSession = async (sessionId: string) => {
  try {
    const response = await api.get(`/chat/sessions/${sessionId}/`)
    const sessionMessages = response.data.messages || []
    
    // 转换消息格式以匹配前端期望的格式
    messages.value = sessionMessages.map((msg: any) => ({
      id: msg.id,
      role: msg.message_type === 'user' ? 'user' : 'assistant',
      content: msg.message_type === 'user' ? msg.question : msg.answer,
      timestamp: new Date(msg.created_at),
      tokens_used: msg.tokens_used,
      isError: msg.message_type === 'assistant' && msg.answer.includes('API调用失败'),
      errorType: msg.message_type === 'assistant' && msg.answer.includes('API调用失败') ? 'error' : 'normal'
    }))
    
    currentSessionId.value = sessionId
    showSessionList.value = false
    nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('加载会话失败:', error)
    ElMessage.error('加载会话失败')
  }
}

// 创建新会话
const createNewSession = () => {
  messages.value = []
  currentSessionId.value = null
  showSessionList.value = false
}

// 删除会话
const deleteSession = async (sessionId: string) => {
  try {
    await api.delete(`/chat/sessions/${sessionId}/delete/`)
    await loadSessions()
    if (currentSessionId.value === sessionId) {
      createNewSession()
    }
    ElMessage.success('会话删除成功')
  } catch (error) {
    console.error('删除会话失败:', error)
    ElMessage.error('删除会话失败')
  }
}

// 处理会话列表关闭
const handleSessionListClose = () => {
  showSessionList.value = false
}

// 知识库变更
const onKnowledgeBaseChange = () => {
  // 可以在这里添加切换知识库时的逻辑
}

// AI提供商变更
const onProviderChange = () => {
  loadAvailableModels()
}

// 模型变更
const onModelChange = () => {
  // 可以在这里添加切换模型时的逻辑
}

// 跳转到配置页面
const goToConfig = () => {
  router.push('/ai-models')
}

// 返回首页
const goBack = () => {
  router.push('/')
}

// 预览检索证据
const previewRetrieval = async () => {
  if (!selectedKnowledgeBase.value) {
    ElMessage.warning('请先选择知识库')
    return
  }
  previewLoading.value = true
  evidence.value = []
  retrievalStats.value = null
  try {
    const resp = await api.post('/knowledge/preview-retrieval/', {
      query: inputMessage.value || '示例问题',
      knowledge_base_id: selectedKnowledgeBase.value,
      strategy: strategy.strategy,
      top_k: strategy.top_k,
      score_threshold: strategy.score_threshold,
      alpha: strategy.alpha
    })
    evidence.value = resp.data?.evidence || []
    retrievalStats.value = {
      total_found: resp.data?.total_found || 0,
      unique_found: resp.data?.unique_found || 0
    }
    if (!evidence.value.length) {
      ElMessage.info('无证据满足当前策略，请调整参数')
    }
  } catch (e) {
    console.error('预览失败', e)
    ElMessage.error('预览失败')
  } finally {
    previewLoading.value = false
  }
}

// 组件挂载
onMounted(() => {
  loadKnowledgeBases()
  loadAIConfig()
  loadRetrievalStrategies()
  loadSessions()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--apple-body-bg);
  position: relative;
  padding: 24px 40px 40px;
}

.chat-header {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-card-radius);
  padding: 0;
  height: 96px;
  position: relative;
  z-index: 10;
  box-shadow: none;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: rgba(10, 132, 255, 0.08);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--apple-brand-blue);
}

.title-text h2 {
  margin: 0;
  color: var(--apple-text-primary);
  font-size: 1.5rem;
  font-weight: 700;
}

.title-text p {
  margin: 0;
  color: var(--apple-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.control-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 1rem 1.5rem;
  box-shadow: none;
  border: 1px solid var(--apple-border);
  display: flex;
  gap: 1.5rem;
  align-items: end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-group label {
  font-size: 0.8rem;
  color: var(--apple-text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.control-select {
  min-width: 140px;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.strategy-form {
  padding: 0.5rem 0.5rem 1rem 0.5rem;
}

.evidence-list {
  margin-top: 1rem;
}

.evidence-stats {
  margin-bottom: 16px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.evidence-stats .el-tag {
  margin-right: 8px;
}

.evidence-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.evidence-title {
  font-weight: 600;
  color: #2c3e50;
}

.evidence-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chat-main {
  flex: 1;
  padding: 0;
  overflow: hidden;
  background: transparent;
}

.chat-messages {
  height: 100%;
  overflow-y: auto;
  padding: 1.5rem;
  scroll-behavior: smooth;
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-card-radius);
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--apple-text-secondary);
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: rgba(10, 132, 255, 0.12);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--apple-brand-blue);
  margin-bottom: 1.5rem;
}

.empty-chat h3 {
  margin: 0 0 0.5rem 0;
  color: var(--apple-text-primary);
  font-size: 1.5rem;
  font-weight: 600;
}

.empty-chat p {
  margin: 0;
  font-size: 1rem;
  opacity: 0.8;
}

.message {
  display: flex;
  margin-bottom: 2rem;
  gap: 1rem;
  animation: messageSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transition: all 0.3s ease;
}

.message:hover {
  transform: translateY(-1px);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--apple-border);
  background: rgba(10, 132, 255, 0.08);
  color: var(--apple-brand-blue);
}

.user-message .message-avatar {
  background: rgba(10, 132, 255, 0.12);
  color: var(--apple-brand-blue);
}

.ai-message .message-avatar {
  background: rgba(52, 199, 89, 0.12);
  color: var(--apple-success);
}

.message-content {
  flex: 1;
  max-width: 75%;
}

.user-message .message-content {
  text-align: right;
}

.message-text {
  background: var(--apple-surface);
  padding: 1rem 1.25rem;
  border-radius: 18px;
  line-height: 1.6;
  word-wrap: break-word;
  border: 1px solid var(--apple-border);
  position: relative;
  overflow: hidden;
}

.message-text::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.7), transparent);
}

.user-message .message-text {
  background: var(--apple-brand-blue);
  color: white;
}

.ai-answer-container {
  width: 100%;
  margin: 0;
  padding: 0;
}

.user-message {
  background: #e3f2fd;
  padding: 12px 16px;
  border-radius: 12px;
  border-bottom-left-radius: 4px;
  color: #1976d2;
  font-weight: 500;
}

.error-message .message-avatar {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  color: white;
  border: 2px solid rgba(245, 108, 108, 0.2);
}

.error-text {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%) !important;
  color: #dc2626 !important;
  border: 1px solid #fecaca !important;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.15) !important;
}

.error-tag {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(245, 108, 108, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  color: #dc2626;
  font-weight: 500;
  font-size: 0.7rem;
}

.message-meta {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #6c757d;
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.user-message .message-meta {
  justify-content: flex-end;
}

.message-tokens {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  color: #667eea;
  font-weight: 500;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  color: #6c757d;
  font-style: italic;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 18px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  position: relative;
  overflow: hidden;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stop-button {
  flex-shrink: 0;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.stop-button:hover {
  opacity: 1;
  transform: scale(1.05);
}

.loading-indicator::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  animation: loadingShimmer 2s infinite;
}

@keyframes loadingShimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.chat-footer {
  background: transparent;
  padding: 24px 0;
}

.input-container {
  max-width: 1400px;
  margin: 0 auto;
}

.input-wrapper {
  display: flex;
  gap: 1rem;
  align-items: end;
  background: #fff;
  border-radius: 20px;
  padding: 1rem;
  box-shadow: none;
  border: 1px solid #ededf0;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  box-shadow: none;
  resize: none;
  font-size: 1rem;
  line-height: 1.5;
  padding: 0.75rem 1rem;
}

.message-input :deep(.el-textarea__inner):focus {
  box-shadow: none;
  border: none;
}

.input-actions {
  display: flex;
  align-items: center;
}

.input-tips {
  margin-top: 0.75rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.tip-warning {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #f56c6c;
  font-size: 0.875rem;
  font-weight: 500;
}

.tip-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-size: 0.875rem;
  font-weight: 500;
}

/* 会话列表对话框样式 */
.session-dialog :deep(.el-dialog) {
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.session-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px 20px 0 0;
  padding: 1.5rem 2rem;
}

.session-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 700;
  font-size: 1.25rem;
}

.session-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 1.5rem;
}

.session-dialog :deep(.el-dialog__body) {
  padding: 2rem;
  background: #f8f9fa;
}

.session-dialog :deep(.el-dialog__footer) {
  background: white;
  border-radius: 0 0 20px 20px;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e1e5e9;
}

.session-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.session-list::-webkit-scrollbar {
  width: 6px;
}

.session-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.session-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.session-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border: 2px solid transparent;
  border-radius: 16px;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.session-item:hover {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.session-item.active {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
}

.session-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
  align-items: center;
}

.session-time,
.session-count {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.last-message {
  font-size: 0.85rem;
  color: #6c757d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  line-height: 1.4;
  background: rgba(102, 126, 234, 0.05);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.session-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.empty-sessions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #6c757d;
  padding: 3rem 2rem;
}

.empty-sessions .empty-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.empty-sessions h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
}

.empty-sessions p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

.dialog-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-content {
    padding: 0 1.5rem;
  }
  
  .control-card {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .control-group {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 1rem;
    flex-direction: column;
    gap: 1rem;
    height: auto;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .header-title {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .title-icon {
    width: 40px;
    height: 40px;
  }
  
  .header-controls {
    width: 100%;
  }
  
  .control-card {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
    padding: 1rem;
  }
  
  .control-group {
    min-width: auto;
  }
  
  .header-actions {
    flex-direction: row;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-main {
    margin: 0.5rem;
    padding: 0.5rem;
    border-radius: 16px;
  }
  
  .chat-messages {
    padding: 1rem;
  }
  
  .input-wrapper {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .input-actions {
    justify-content: center;
  }
  
  .input-tips {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .chat-container {
    height: 100vh;
    height: 100dvh; /* 动态视口高度 */
  }
  
  .header-content {
    padding: 0.75rem;
  }
  
  .title-text h2 {
    font-size: 1.25rem;
  }
  
  .title-text p {
    font-size: 0.8rem;
  }
  
  .control-card {
    padding: 0.75rem;
  }
  
  .chat-main {
    margin: 0.25rem;
    padding: 0.25rem;
    border-radius: 12px;
  }
  
  .chat-messages {
    padding: 0.75rem;
  }
  
  .message {
    margin-bottom: 1.5rem;
    gap: 0.75rem;
  }
  
  .message-avatar {
    width: 36px;
    height: 36px;
  }
  
  .message-text {
    padding: 0.75rem 1rem;
    border-radius: 16px;
  }
  
  .chat-footer {
    padding: 1rem;
  }
  
  .input-wrapper {
    padding: 0.75rem;
  }
  
  .session-dialog :deep(.el-dialog) {
    width: 95%;
    margin: 0 auto;
  }
  
  .session-dialog :deep(.el-dialog__header) {
    padding: 1rem 1.5rem;
  }
  
  .session-dialog :deep(.el-dialog__body) {
    padding: 1.5rem;
  }
  
  .session-dialog :deep(.el-dialog__footer) {
    padding: 1rem 1.5rem;
  }
  
  .session-item {
    padding: 1rem;
    gap: 0.75rem;
  }
  
  .session-avatar {
    width: 40px;
    height: 40px;
  }
  
  .session-meta {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .dialog-footer {
    flex-direction: column;
    gap: 0.75rem;
  }
}
</style>