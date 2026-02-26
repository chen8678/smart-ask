<template>
  <div class="voice-qa-container">
    <div class="header">
      <h2>🎤 语音智能问答</h2>
      <p class="subtitle">语音唤醒，智能回答，语音播报</p>
    </div>

    <!-- 知识库选择 -->
    <div class="kb-selector">
      <el-select 
        v-model="selectedKnowledgeBase" 
        placeholder="选择知识库"
        style="width: 100%"
        @change="handleKbChange"
      >
        <el-option
          v-for="kb in knowledgeBases"
          :key="kb.id"
          :label="kb.name"
          :value="kb.id"
        />
      </el-select>
    </div>

    <!-- 语音输入区域 -->
    <div class="voice-input-section">
      <div class="voice-controls">
        <el-button
          :type="isRecording ? 'danger' : 'primary'"
          :icon="isRecording ? 'VideoPause' : 'Microphone'"
          circle
          size="large"
          @click="toggleRecording"
          :loading="processing"
        >
        </el-button>
        <span class="status-text">{{ statusText }}</span>
      </div>
      
      <div v-if="recognizedText" class="recognized-text">
        <p><strong>识别的问题：</strong>{{ recognizedText }}</p>
      </div>
    </div>

    <!-- 问答结果 -->
    <div v-if="result" class="result-section">
      <div class="result-header">
        <el-tag type="success" size="small">私有知识库</el-tag>
        <span class="result-label">专业准确</span>
      </div>
      
      <div class="answer-section">
        <h3>答案：</h3>
        <div class="answer-content">{{ result.answer }}</div>
        
        <!-- 语音播放控制 -->
        <div v-if="result.audio_data" class="audio-controls">
          <el-button
            type="primary"
            :icon="isPlaying ? 'VideoPause' : 'VideoPlay'"
            @click="togglePlayAudio"
            :loading="loadingAudio"
          >
            {{ isPlaying ? '暂停播放' : '播放语音回答' }}
          </el-button>
        </div>
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

    <!-- 错误提示 -->
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
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const selectedKnowledgeBase = ref('')
const knowledgeBases = ref<any[]>([])
const isRecording = ref(false)
const processing = ref(false)
const recognizedText = ref('')
const result = ref<any>(null)
const error = ref('')
const statusText = ref('点击麦克风开始录音')
const isPlaying = ref(false)
const loadingAudio = ref(false)
const audioContext: any = ref(null)
const audioSource: any = ref(null)

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const response = await api.get('/knowledge/')
    knowledgeBases.value = response.data.results || response.data || []
    if (knowledgeBases.value.length > 0) {
      selectedKnowledgeBase.value = knowledgeBases.value[0].id
    }
  } catch (err: any) {
    console.error('加载知识库失败:', err)
  }
}

const handleKbChange = () => {
  console.log('选择知识库:', selectedKnowledgeBase.value)
}

// 开始/停止录音
const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data)
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
      await processAudio(audioBlob)
      
      // 停止所有音频轨道
      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.start()
    isRecording.value = true
    statusText.value = '正在录音...（点击停止）'
  } catch (err: any) {
    ElMessage.error('无法访问麦克风: ' + err.message)
    error.value = '无法访问麦克风，请检查浏览器权限设置'
  }
}

const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    statusText.value = '正在处理...'
    processing.value = true
  }
}

// 处理音频并发送语音问答请求
const processAudio = async (audioBlob: Blob) => {
  try {
    // 转换为base64
    const reader = new FileReader()
    reader.onloadend = async () => {
      const base64Audio = (reader.result as string).split(',')[1]
      
      try {
        const response = await api.post('/chat/voice/qa/', {
          audio_data: base64Audio,
          knowledge_base_id: selectedKnowledgeBase.value || undefined
        })
        
        result.value = response.data
        recognizedText.value = response.data.question || ''
        error.value = ''
        
        // 自动播放语音回答
        if (response.data.audio_data) {
          playAudio(response.data.audio_data)
        }
        
        ElMessage.success('问答完成')
      } catch (err: any) {
        error.value = err.response?.data?.error || '语音问答失败'
        ElMessage.error(error.value)
      } finally {
        processing.value = false
        statusText.value = '点击麦克风开始录音'
      }
    }
    reader.readAsDataURL(audioBlob)
  } catch (err: any) {
    processing.value = false
    error.value = '处理音频失败: ' + err.message
    ElMessage.error(error.value)
  }
}

// 播放音频
const playAudio = async (audioBase64: string) => {
  try {
    loadingAudio.value = true
    
    // 解码base64
    const audioData = atob(audioBase64)
    const audioArray = new Uint8Array(audioData.length)
    for (let i = 0; i < audioData.length; i++) {
      audioArray[i] = audioData.charCodeAt(i)
    }
    
    // 创建音频对象
    const audioBlob = new Blob([audioArray], { type: 'audio/mp3' })
    const audioUrl = URL.createObjectURL(audioBlob)
    
    const audio = new Audio(audioUrl)
    audio.onended = () => {
      isPlaying.value = false
      URL.revokeObjectURL(audioUrl)
    }
    audio.onerror = () => {
      isPlaying.value = false
      loadingAudio.value = false
      ElMessage.error('播放音频失败')
    }
    
    await audio.play()
    isPlaying.value = true
    loadingAudio.value = false
  } catch (err: any) {
    loadingAudio.value = false
    ElMessage.error('播放音频失败: ' + err.message)
  }
}

const togglePlayAudio = () => {
  if (result.value && result.value.audio_data) {
    if (isPlaying.value) {
      // 停止播放
      isPlaying.value = false
    } else {
      playAudio(result.value.audio_data)
    }
  }
}

onMounted(() => {
  loadKnowledgeBases()
})

onUnmounted(() => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
  }
})
</script>

<style scoped>
.voice-qa-container {
  max-width: 900px;
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

.kb-selector {
  margin-bottom: 30px;
}

.voice-input-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 30px;
  text-align: center;
}

.voice-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.status-text {
  color: #606266;
  font-size: 14px;
}

.recognized-text {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
  text-align: left;
}

.recognized-text p {
  margin: 0;
  color: #606266;
}

.result-section {
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
  margin-bottom: 15px;
}

.audio-controls {
  margin-top: 15px;
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

