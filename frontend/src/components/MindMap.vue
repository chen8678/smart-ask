<template>
  <div class="mind-map-container">
    <div class="mind-map-header">
      <h3>{{ title }}</h3>
      <div class="mind-map-actions">
        <el-button size="small" @click="zoomIn">
          <el-icon><ZoomIn /></el-icon>
          放大
        </el-button>
        <el-button size="small" @click="zoomOut">
          <el-icon><ZoomOut /></el-icon>
          缩小
        </el-button>
        <el-button size="small" @click="resetZoom">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
        <el-button size="small" @click="downloadImage">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>
    <div ref="mindMapRef" class="mind-map-svg"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { ElMessage } from 'element-plus'

interface MindMapNode {
  name: string
  children?: MindMapNode[]
  value?: number
  level?: number
}

interface Props {
  data: MindMapNode
  title?: string
  width?: number
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '思维导图',
  width: 800,
  height: 600
})

const mindMapRef = ref<HTMLElement>()
let svg: d3.Selection<SVGSVGElement, unknown, null, undefined>
let g: d3.Selection<SVGGElement, unknown, null, undefined>
let zoom: d3.ZoomBehavior<SVGSVGElement, unknown>
let currentScale = 1

const initMindMap = () => {
  if (!mindMapRef.value || !props.data) return

  // 清除之前的内容
  d3.select(mindMapRef.value).selectAll('*').remove()

  // 创建SVG
  svg = d3.select(mindMapRef.value)
    .append('svg')
    .attr('width', props.width)
    .attr('height', props.height)
    .style('background', '#fafafa')
    .style('border-radius', '8px')

  // 创建主组
  g = svg.append('g')

  // 设置缩放行为
  zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.1, 3])
    .on('zoom', (event) => {
      currentScale = event.transform.k
      g.attr('transform', event.transform)
    })

  svg.call(zoom)

  // 创建层次布局
  const tree = d3.tree<MindMapNode>()
    .size([props.height - 100, props.width - 100])
    .separation((a, b) => (a.parent === b.parent ? 1 : 2) / a.depth)

  // 准备数据
  const root = d3.hierarchy(props.data)
  const treeData = tree(root)

  // 添加连接线
  g.selectAll('.link')
    .data(treeData.links())
    .enter()
    .append('path')
    .attr('class', 'link')
    .attr('d', d3.linkHorizontal<any, any>()
      .x(d => d.y + 50)
      .y(d => d.x + 50))
    .style('fill', 'none')
    .style('stroke', '#999')
    .style('stroke-width', 2)
    .style('opacity', 0.6)

  // 添加节点组
  const node = g.selectAll('.node')
    .data(treeData.descendants())
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr('transform', d => `translate(${d.y + 50},${d.x + 50})`)
    .style('cursor', 'pointer')

  // 添加节点圆圈
  node.append('circle')
    .attr('r', d => d.depth === 0 ? 12 : 8)
    .style('fill', d => d.depth === 0 ? '#409eff' : '#67c23a')
    .style('stroke', '#fff')
    .style('stroke-width', 2)

  // 添加节点文本
  node.append('text')
    .attr('dy', d => d.depth === 0 ? 25 : 20)
    .attr('text-anchor', 'middle')
    .style('font-size', d => d.depth === 0 ? '14px' : '12px')
    .style('font-weight', d => d.depth === 0 ? 'bold' : 'normal')
    .style('fill', '#333')
    .text(d => d.data.name)
    .each(function(d) {
      // 文本换行处理
      const text = d3.select(this)
      const words = d.data.name.split(' ')
      if (words.length > 2) {
        text.text(null)
        words.forEach((word, i) => {
          text.append('tspan')
            .attr('x', 0)
            .attr('dy', i === 0 ? 0 : '1.2em')
            .text(word)
        })
      }
    })

  // 添加节点点击事件
  node.on('click', (event, d) => {
    if (d.children) {
      d._children = d.children
      d.children = null
    } else {
      d.children = d._children
      d._children = null
    }
    update(d)
  })

  // 添加悬停效果
  node.on('mouseover', function(event, d) {
    d3.select(this).select('circle')
      .style('stroke', '#409eff')
      .style('stroke-width', 3)
  })
  .on('mouseout', function(event, d) {
    d3.select(this).select('circle')
      .style('stroke', '#fff')
      .style('stroke-width', 2)
  })

  // 更新函数
  function update(source: any) {
    const treeData = tree(root)
    
    // 更新节点位置
    const nodes = treeData.descendants()
    const links = treeData.links()

    // 更新连接线
    g.selectAll('.link')
      .data(links)
      .transition()
      .duration(300)
      .attr('d', d3.linkHorizontal<any, any>()
        .x(d => d.y + 50)
        .y(d => d.x + 50))

    // 更新节点
    const node = g.selectAll('.node')
      .data(nodes, (d: any) => d.id || (d.id = ++(d as any).i))

    // 移除退出节点
    node.exit()
      .transition()
      .duration(300)
      .attr('transform', d => `translate(${source.y + 50},${source.x + 50})`)
      .style('opacity', 0)
      .remove()

    // 添加新节点
    const nodeEnter = node.enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${source.y + 50},${source.x + 50})`)
      .style('opacity', 0)
      .style('cursor', 'pointer')

    nodeEnter.append('circle')
      .attr('r', d => d.depth === 0 ? 12 : 8)
      .style('fill', d => d.depth === 0 ? '#409eff' : '#67c23a')
      .style('stroke', '#fff')
      .style('stroke-width', 2)

    nodeEnter.append('text')
      .attr('dy', d => d.depth === 0 ? 25 : 20)
      .attr('text-anchor', 'middle')
      .style('font-size', d => d.depth === 0 ? '14px' : '12px')
      .style('font-weight', d => d.depth === 0 ? 'bold' : 'normal')
      .style('fill', '#333')
      .text(d => d.data.name)

    // 更新所有节点位置
    node.merge(nodeEnter as any)
      .transition()
      .duration(300)
      .attr('transform', d => `translate(${d.y + 50},${d.x + 50})`)
      .style('opacity', 1)
  }

  // 居中显示
  const bounds = g.node()?.getBBox()
  if (bounds) {
    const fullWidth = props.width
    const fullHeight = props.height
    const width = bounds.width
    const height = bounds.height
    const midX = bounds.x + width / 2
    const midY = bounds.y + height / 2
    
    if (width < fullWidth && height < fullHeight) {
      const scale = 0.95 / Math.max(width / fullWidth, height / fullHeight)
      const translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY]
      svg.transition().duration(750).call(
        zoom.transform as any,
        d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
      )
    }
  }
}

const zoomIn = () => {
  svg.transition().duration(300).call(
    zoom.scaleBy as any,
    1.5
  )
}

const zoomOut = () => {
  svg.transition().duration(300).call(
    zoom.scaleBy as any,
    1 / 1.5
  )
}

const resetZoom = () => {
  svg.transition().duration(300).call(
    zoom.transform as any,
    d3.zoomIdentity
  )
}

const downloadImage = () => {
  if (!svg.node()) return
  
  const svgData = new XMLSerializer().serializeToString(svg.node()!)
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  const img = new Image()
  
  canvas.width = props.width
  canvas.height = props.height
  
  img.onload = () => {
    ctx?.drawImage(img, 0, 0)
    const link = document.createElement('a')
    link.download = `${props.title || 'mind-map'}.png`
    link.href = canvas.toDataURL()
    link.click()
  }
  
  img.src = 'data:image/svg+xml;base64,' + btoa(svgData)
  ElMessage.success('思维导图已导出')
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    initMindMap()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    initMindMap()
  })
})
</script>

<style scoped>
.mind-map-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mind-map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  border-radius: 8px 8px 0 0;
}

.mind-map-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.mind-map-actions {
  display: flex;
  gap: 8px;
}

.mind-map-svg {
  flex: 1;
  background: #fafafa;
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

:deep(.link) {
  fill: none;
  stroke: #999;
  stroke-width: 2;
  opacity: 0.6;
}

:deep(.node circle) {
  cursor: pointer;
  transition: all 0.3s ease;
}

:deep(.node circle:hover) {
  stroke: #409eff !important;
  stroke-width: 3 !important;
}

:deep(.node text) {
  pointer-events: none;
  user-select: none;
}
</style>
