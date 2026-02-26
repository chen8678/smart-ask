<template>
  <div class="ai-model-config">
    <el-header class="config-header">
      <div class="header-content">
        <h2>AI模型配置</h2>
        <el-button @click="goBack" class="ghost-btn">
          <AppleIcon name="chevron.backward" :size="16" />
          返回
        </el-button>
      </div>
    </el-header>

    <el-main class="config-main">
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <span>模型配置</span>
            <el-button @click="refreshModels" size="small" class="ghost-btn">
              <AppleIcon name="arrow.clockwise" :size="14" />
              刷新
            </el-button>
          </div>
        </template>

        <div class="provider-list">
          <div 
            v-for="provider in providers" 
            :key="provider.key"
            class="provider-item"
            :class="{ 'provider-available': provider.available, 'provider-unavailable': !provider.available }"
          >
            <div class="provider-info">
              <div class="provider-name">
                <span
                  class="status-dot"
                  :class="provider.available ? 'status-success' : 'status-error'"
                >
                  <AppleIcon
                    :name="provider.available ? 'checkmark.seal.fill' : 'xmark.seal'"
                    :size="16"
                  />
                </span>
                <span class="provider-title">{{ provider.name }}</span>
                <el-tag :type="provider.available ? 'success' : 'danger'" size="small" class="status-tag">
                  <AppleIcon
                    :name="provider.available ? 'dot.radiowaves.left.and.right' : 'exclamationmark.triangle'"
                    :size="12"
                  />
                  {{ provider.available ? '已配置' : '配置失败' }}
                </el-tag>
              </div>
              <div class="provider-description">
                {{ getProviderDescription(provider.key) }}
              </div>
              <div class="provider-details">
                <span class="provider-api">API: {{ provider.api_base }}</span>
                <span class="provider-models">模型数: {{ provider.models.length }}</span>
              </div>
            </div>
            <div class="provider-actions">
              <el-button 
                @click="configureProvider(provider)" 
                :type="provider.available ? 'warning' : 'primary'" 
                size="small"
              >
                {{ provider.available ? '重新配置' : '配置API Key' }}
              </el-button>
              <el-button 
                v-if="provider.available" 
                @click="viewModels(provider)" 
                type="success" 
                size="small"
              >
                查看模型
              </el-button>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 配置对话框 -->
      <el-dialog
        v-model="showConfigDialog"
        :title="`配置 ${currentProvider?.name} API Key`"
        width="600px"
      >
        <div class="config-content">
          <div class="provider-info-card">
            <div class="provider-icon">
              <AppleIcon name="cpu" :size="28" />
            </div>
            <div class="provider-details">
              <h3>{{ currentProvider?.name }}</h3>
              <p>{{ getProviderDescription(currentProvider?.key) }}</p>
              <div class="api-info">
                <span class="api-url">{{ currentProvider?.api_base }}</span>
              </div>
            </div>
          </div>
          
          <el-form :model="configForm" label-width="100px" class="config-form">
            <el-form-item label="API Key" required>
              <el-input
                v-model="configForm.api_key"
                type="password"
                placeholder="请输入您的API Key（例如：sk-xxxxxxxxxxxxxxxx）"
                show-password
                size="large"
                class="api-key-input"
                clearable
              >
                <template #prefix>
                  <AppleIcon name="key.fill" :size="14" />
                </template>
              </el-input>
              <div class="form-tip">
                <AppleIcon name="info.circle" :size="14" />
                <span>请确保API Key有效且有足够的额度</span>
              </div>
            </el-form-item>
            
            <el-form-item label="当前状态">
              <el-tag :type="currentProvider?.available ? 'success' : 'danger'" size="large">
                <AppleIcon :name="currentProvider?.available ? 'antenna.radiowaves.left.and.right' : 'exclamationmark.triangle'" :size="12" />
                {{ currentProvider?.available ? '已配置' : '配置失败' }}
              </el-tag>
            </el-form-item>
          </el-form>
          
          <div class="config-tips">
            <el-alert
              title="配置说明"
              type="info"
              :closable="false"
            >
              <div class="tip-content">
                <p><strong>1. 获取API Key：</strong></p>
                <ul>
                  <li v-if="currentProvider?.key === 'deepseek'">
                    DeepSeek: 访问 <a href="https://platform.deepseek.com/" target="_blank">https://platform.deepseek.com/</a> 注册并获取API Key
                  </li>
                  <li v-if="currentProvider?.key === 'qwen'">
                    通义千问: 访问 <a href="https://dashscope.aliyun.com/" target="_blank">https://dashscope.aliyun.com/</a> 注册并获取API Key
                  </li>
                  <li v-if="currentProvider?.key === 'glm'">
                    GLM: 访问 <a href="https://open.bigmodel.cn/" target="_blank">https://open.bigmodel.cn/</a> 注册并获取API Key
                  </li>
                </ul>
                <p><strong>2. 测试连接：</strong>配置完成后请先测试连接确保API Key有效</p>
                <p><strong>3. 开始使用：</strong>配置成功后即可在聊天和学习内容生成中使用该模型</p>
              </div>
            </el-alert>
          </div>
        </div>
        <template #footer>
          <el-button @click="showConfigDialog = false">取消</el-button>
          <el-button @click="saveConfig" type="primary" :loading="testing">
            {{ testing ? '测试中...' : '测试并保存' }}
          </el-button>
        </template>
      </el-dialog>

      <!-- 模型列表对话框 -->
      <el-dialog
        v-model="showModelsDialog"
        :title="`${currentProvider?.name} 可用模型`"
        width="800px"
      >
        <div class="models-list">
          <div 
            v-for="model in providerModels" 
            :key="model.key"
            class="model-item"
          >
            <div class="model-info">
              <div class="model-name">{{ model.name }}</div>
              <div class="model-version">版本: {{ model.version }}</div>
            </div>
            <div class="model-actions">
              <el-button @click="selectModel(model)" type="primary" size="small">
                选择此模型
              </el-button>
            </div>
          </div>
        </div>
        <template #footer>
          <el-button @click="showModelsDialog = false">关闭</el-button>
        </template>
      </el-dialog>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppleIcon from '@/components/AppleIcon.vue'
import api from '@/utils/api'

const router = useRouter()

interface Provider {
  key: string
  name: string
  api_base: string
  available: boolean
  models: string[]
}

interface Model {
  key: string
  name: string
  version: string
  provider: string
}

const providers = ref<Provider[]>([])
const currentProvider = ref<Provider | null>(null)
const providerModels = ref<Model[]>([])

const showConfigDialog = ref(false)
const showModelsDialog = ref(false)
const configForm = ref({
  api_key: '',
  provider_key: ''
})
const testResult = ref('')
const saving = ref(false)
const testing = ref(false)

onMounted(() => {
  loadProviders()
})

const loadProviders = async () => {
  try {
    const response = await api.get('/chat/providers/')
    providers.value = response.data
  } catch (error) {
    console.warn('加载提供商列表失败')
    ElMessage.error('加载提供商列表失败')
  }
}

const getProviderDescription = (providerKey: string) => {
  const descriptions: Record<string, string> = {
    'deepseek': 'DeepSeek公司开发的大语言模型，擅长代码生成和数学推理',
    'qwen': '阿里巴巴开发的大语言模型，在中文理解和生成方面表现优秀',
    'glm': '智谱AI开发的多模态大语言模型，支持文本和图像理解'
  }
  return descriptions[providerKey] || 'AI模型提供商'
}

const refreshModels = () => {
  loadProviders()
  ElMessage.success('提供商状态已刷新')
}

const configureProvider = (provider: Provider) => {
  currentProvider.value = provider
  configForm.value = {
    api_key: '',
    provider_key: provider.key
  }
  showConfigDialog.value = true
}

const saveConfig = async () => {
  if (!currentProvider.value) return
  
  testing.value = true
  try {
    // 先测试API Key
    const testResponse = await api.post('/chat/test-api-key/', {
      provider_key: configForm.value.provider_key,
      api_key: configForm.value.api_key
    })
    
    if (!testResponse.data.success) {
      ElMessage.error(`API Key测试失败: ${testResponse.data.error}`)
      // 刷新提供商列表以更新状态
      loadProviders()
      return
    }
    
    // 保存API Key
    const saveResponse = await api.post('/chat/save-api-key/', {
      provider_key: configForm.value.provider_key,
      api_key: configForm.value.api_key
    })
    
    ElMessage.success('API Key配置成功！')
    showConfigDialog.value = false
    loadProviders()
  } catch (error: any) {
    console.error('配置失败:', error)
    let errorMessage = '配置失败'
    
    if (error.response?.data?.error) {
      errorMessage = `配置失败: ${error.response.data.error}`
    } else if (error.message) {
      errorMessage = `配置失败: ${error.message}`
    }
    
    ElMessage.error(errorMessage)
    // 刷新提供商列表以更新状态
    loadProviders()
  } finally {
    testing.value = false
  }
}

const viewModels = async (provider: Provider) => {
  currentProvider.value = provider
  try {
    const response = await api.get(`/chat/providers/${provider.key}/models/`)
    providerModels.value = response.data
    showModelsDialog.value = true
  } catch (error) {
    ElMessage.error('加载模型列表失败')
  }
}

const selectModel = (model: Model) => {
  ElMessage.success(`已选择模型: ${model.name}`)
  showModelsDialog.value = false
  // 这里可以跳转到聊天页面并设置默认模型
  router.push('/chat')
}

const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.ai-model-config {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--apple-background);
  padding: 32px 48px 64px;
  font-family: var(--apple-font-family, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif);
}

.config-header {
  background: var(--apple-surface);
  border: var(--apple-border);
  border-radius: 24px;
  padding: 0;
  margin-bottom: 24px;
  box-shadow: var(--apple-card-shadow);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 32px;
}

.header-content h2 {
  color: var(--apple-text-primary);
  margin: 0;
  font-weight: 600;
}

:deep(.ghost-btn.el-button) {
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.85);
  color: var(--apple-text-primary);
  display: inline-flex;
  gap: 6px;
  align-items: center;
  padding: 0 18px;
}

:deep(.ghost-btn.el-button:hover) {
  background: #f2f2f7;
}

.config-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.config-card {
  max-width: 1000px;
  margin: 0 auto;
  background: var(--apple-surface);
  border: var(--apple-border);
  border-radius: 24px;
  padding: 32px;
  box-shadow: var(--apple-card-shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 24px;
  background: var(--apple-elevated);
  transition: transform 0.2s ease, border-color 0.2s ease;
  box-shadow: var(--apple-card-shadow);
}

.provider-item:hover {
  transform: translateY(-2px);
}

.provider-available {
  border-color: rgba(52, 199, 89, 0.4);
}

.provider-unavailable {
  border-color: rgba(255, 59, 48, 0.2);
}

.provider-info {
  flex: 1;
}

.provider-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.status-dot {
  width: 32px;
  height: 32px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--apple-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.provider-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--apple-text-primary);
}

.provider-description {
  color: var(--apple-text-secondary);
  margin-bottom: 8px;
  line-height: 1.5;
}

.provider-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--apple-text-tertiary);
}

.provider-api,
.provider-models {
  background: rgba(118, 118, 128, 0.08);
  padding: 2px 8px;
  border-radius: 8px;
}

.provider-actions {
  display: flex;
  gap: 8px;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.models-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.model-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  background: var(--apple-surface);
  box-shadow: var(--apple-card-shadow);
}

.model-info {
  flex: 1;
}

.model-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin-bottom: 4px;
}

.model-version {
  font-size: 12px;
  color: var(--apple-text-tertiary);
}

.model-actions {
  display: flex;
  gap: 8px;
}

.config-tips {
  margin-top: 16px;
}

.status-success {
  color: #34c759;
}

.status-error {
  color: #ff3b30;
}

.test-result {
  margin-top: 16px;
  padding: 16px;
  background: var(--apple-elevated);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.test-result h4 {
  margin: 0 0 8px 0;
  color: var(--apple-text-primary);
}

.result-content {
  color: var(--apple-text-secondary);
  line-height: 1.5;
  white-space: pre-wrap;
}

/* 新增样式 */
.config-content {
  padding: 20px 0;
}

.provider-info-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: var(--apple-elevated);
  border-radius: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  gap: 16px;
}

.provider-icon {
  width: 56px;
  height: 56px;
  border-radius: 20px;
  background: linear-gradient(135deg, #0A84FF, #5AC8FA);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.provider-details h3 {
  margin: 0 0 8px 0;
  color: var(--apple-text-primary);
  font-size: 18px;
  font-weight: 600;
}

.provider-details p {
  margin: 0 0 12px 0;
  color: var(--apple-text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

.api-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.api-url {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: var(--apple-text-secondary);
  background: rgba(118, 118, 128, 0.16);
  padding: 6px 10px;
  border-radius: 8px;
}

.config-form {
  margin: 24px 0;
}

.api-key-input {
  margin-bottom: 8px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--apple-text-tertiary);
  margin-top: 8px;
}

.tip-content {
  line-height: 1.6;
}

.tip-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.tip-content li {
  margin: 4px 0;
}

.tip-content a {
  color: #0A84FF;
  text-decoration: none;
}

.tip-content a:hover {
  text-decoration: underline;
}

</style>

