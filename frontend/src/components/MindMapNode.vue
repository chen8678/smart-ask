<!-- 思维导图节点组件 -->
<template>
  <div class="mindmap-node" :class="nodeClasses" @click="handleClick">
    <!-- 节点内容 -->
    <div class="node-content">
      <div class="node-text">{{ node.text }}</div>
      <div v-if="nodeMetadata" class="node-metadata">
        <el-tag v-if="node.importance" size="small" type="info">
          {{ node.importance }}%
        </el-tag>
        <el-tag v-if="node.frequency" size="small" type="warning">
          {{ node.frequency }}
        </el-tag>
        <el-tag v-if="node.weight" size="small" type="success">
          {{ node.weight }}
        </el-tag>
      </div>
    </div>

    <!-- 子节点 -->
    <div v-if="hasChildren" class="node-children">
      <div class="children-container" :style="childrenStyle">
        <MindMapNode
          v-for="child in node.children"
          :key="child.id"
          :node="child"
          :level="level + 1"
          @node-click="$emit('node-click', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
const props = defineProps<{
  node: any
  level: number
}>()

// Emits
const emit = defineEmits<{
  'node-click': [node: any]
}>()

// 计算属性
const nodeClasses = computed(() => {
  return [
    `node-level-${props.level}`,
    `node-type-${props.node.type}`,
    {
      'has-children': hasChildren.value,
      'is-root': props.level === 0
    }
  ]
})

const hasChildren = computed(() => {
  return props.node.children && props.node.children.length > 0
})

const nodeMetadata = computed(() => {
  return props.node.importance || props.node.frequency || props.node.weight
})

const childrenStyle = computed(() => {
  if (!hasChildren.value) return {}
  
  const childCount = props.node.children.length
  const maxWidth = Math.min(300, childCount * 150) // 限制最大宽度
  
  return {
    maxWidth: `${maxWidth}px`,
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px'
  }
})

// 方法
const handleClick = () => {
  emit('node-click', props.node)
}
</script>

<style scoped>
.mindmap-node {
  display: inline-block;
  margin: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mindmap-node:hover {
  transform: scale(1.05);
}

.node-content {
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 120px;
  text-align: center;
}

.node-content:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.node-text {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  word-break: break-word;
}

.node-metadata {
  display: flex;
  justify-content: center;
  gap: 4px;
  flex-wrap: wrap;
}

.node-children {
  margin-top: 15px;
  position: relative;
}

.children-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

/* 不同级别的样式 */
.node-level-0 .node-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  font-size: 16px;
  font-weight: 600;
  padding: 16px 20px;
}

.node-level-1 .node-content {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-color: #f093fb;
  font-size: 15px;
  font-weight: 500;
}

.node-level-2 .node-content {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-color: #4facfe;
}

.node-level-3 .node-content {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
  border-color: #43e97b;
}

/* 不同类型节点的样式 */
.node-type-root .node-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  font-weight: 700;
  padding: 20px 24px;
}

.node-type-branch .node-content {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  font-weight: 600;
}

.node-type-topic .node-content {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.node-type-concept .node-content {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.node-type-keyword .node-content {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
}

.node-type-empty .node-content {
  background: #f5f7fa;
  color: #909399;
  border-style: dashed;
}

.node-type-error .node-content {
  background: #fef0f0;
  color: #f56c6c;
  border-color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .node-content {
    min-width: 100px;
    padding: 8px 12px;
  }
  
  .node-text {
    font-size: 12px;
  }
  
  .children-container {
    flex-direction: column;
    align-items: center;
  }
}
