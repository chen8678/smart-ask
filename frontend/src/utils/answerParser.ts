/**
 * AI回答内容解析器
 * 用于解析和结构化AI回答内容
 */

export interface ParsedAnswer {
  summary: string;           // 回答摘要
  sections: AnswerSection[]; // 结构化章节
  sources: Source[];         // 引用来源
  confidence: number;        // 置信度
  rawContent: string;        // 原始内容
}

export interface AnswerSection {
  title: string;
  content: string;
  type: 'text' | 'list' | 'code' | 'table' | 'quote';
  level: number;            // 标题级别
  id: string;              // 用于导航
}

export interface Source {
  title: string;
  relevance: number;        // 相关性分数
  preview: string;          // 内容预览
  url?: string;             // 来源链接
}

/**
 * 解析AI回答内容
 */
export function parseAnswer(content: string): ParsedAnswer {
  const summary = extractSummary(content);
  const sections = parseSections(content);
  const sources = extractSources(content);
  const confidence = calculateConfidence(content, sources);

  return {
    summary,
    sections,
    sources,
    confidence,
    rawContent: content
  };
}

/**
 * 提取回答摘要
 */
function extractSummary(content: string): string {
  // 提取第一段作为摘要
  const paragraphs = content.split('\n\n').filter(p => p.trim());
  if (paragraphs.length === 0) return '';
  
  const firstParagraph = paragraphs[0].trim();
  
  // 如果第一段太长，截取前100个字符
  if (firstParagraph.length > 100) {
    return firstParagraph.substring(0, 100) + '...';
  }
  
  return firstParagraph;
}

/**
 * 解析内容章节
 */
function parseSections(content: string): AnswerSection[] {
  const sections: AnswerSection[] = [];
  const lines = content.split('\n');
  
  let currentSection: AnswerSection | null = null;
  let sectionIndex = 0;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 检测标题
    const titleMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (titleMatch) {
      // 保存上一章节
      if (currentSection) {
        currentSection.content = currentSection.content.trim();
        sections.push(currentSection);
      }
      
      // 开始新章节
      const level = titleMatch[1].length;
      const title = titleMatch[2];
      sectionIndex++;
      
      currentSection = {
        title,
        content: '',
        type: 'text',
        level,
        id: `section-${sectionIndex}`
      };
    } else if (currentSection) {
      // 添加到当前章节
      currentSection.content += line + '\n';
    } else {
      // 如果没有当前章节，创建一个默认章节
      if (sections.length === 0) {
        currentSection = {
          title: '回答内容',
          content: line + '\n',
          type: 'text',
          level: 1,
          id: 'section-1'
        };
        sectionIndex = 1;
      } else {
        // 添加到最后一个章节
        const lastSection = sections[sections.length - 1];
        lastSection.content += line + '\n';
      }
    }
  }
  
  // 保存最后一个章节
  if (currentSection) {
    currentSection.content = currentSection.content.trim();
    sections.push(currentSection);
  }
  
  // 检测每个章节的类型
  sections.forEach(section => {
    section.type = detectSectionType(section.content);
  });
  
  return sections;
}

/**
 * 检测章节类型
 */
function detectSectionType(content: string): AnswerSection['type'] {
  const trimmedContent = content.trim();
  
  // 检测代码块
  if (trimmedContent.includes('```') || trimmedContent.includes('`')) {
    return 'code';
  }
  
  // 检测列表
  if (trimmedContent.match(/^[\s]*[-*+]\s/m) || trimmedContent.match(/^[\s]*\d+\.\s/m)) {
    return 'list';
  }
  
  // 检测表格
  if (trimmedContent.includes('|') && trimmedContent.includes('---')) {
    return 'table';
  }
  
  // 检测引用
  if (trimmedContent.startsWith('>')) {
    return 'quote';
  }
  
  return 'text';
}

/**
 * 提取引用来源
 */
function extractSources(content: string): Source[] {
  const sources: Source[] = [];
  
  // 匹配markdown格式的来源引用
  const sourceRegex = /\*\*(.+?\.md)\*\*/g;
  let match;
  
  while ((match = sourceRegex.exec(content)) !== null) {
    const title = match[1];
    const preview = extractPreview(content, title);
    
    sources.push({
      title,
      relevance: calculateRelevance(content, title),
      preview,
      url: `#${title}`
    });
  }
  
  // 如果没有找到来源，尝试其他格式
  if (sources.length === 0) {
    // 匹配 "来源：" 格式
    const sourcePattern = /来源[：:]\s*(.+?)(?:\n|$)/g;
    while ((match = sourcePattern.exec(content)) !== null) {
      const title = match[1].trim();
      sources.push({
        title,
        relevance: 0.8,
        preview: extractPreview(content, title),
        url: `#${title}`
      });
    }
  }
  
  return sources;
}

/**
 * 提取内容预览
 */
function extractPreview(content: string, sourceTitle: string): string {
  // 在内容中查找包含来源标题的段落
  const paragraphs = content.split('\n\n');
  
  for (const paragraph of paragraphs) {
    if (paragraph.includes(sourceTitle)) {
      // 返回该段落的前100个字符
      return paragraph.substring(0, 100) + (paragraph.length > 100 ? '...' : '');
    }
  }
  
  return '相关内容预览';
}

/**
 * 计算来源相关性
 */
function calculateRelevance(content: string, sourceTitle: string): number {
  // 简单的相关性计算：基于来源在内容中的出现频率
  const occurrences = (content.match(new RegExp(sourceTitle, 'g')) || []).length;
  return Math.min(0.9, 0.5 + (occurrences * 0.1));
}

/**
 * 计算回答置信度
 */
function calculateConfidence(content: string, sources: Source[]): number {
  let confidence = 0.5; // 基础置信度
  
  // 基于内容长度调整
  if (content.length > 200) confidence += 0.1;
  if (content.length > 500) confidence += 0.1;
  
  // 基于来源数量调整
  if (sources.length > 0) confidence += 0.1;
  if (sources.length > 2) confidence += 0.1;
  
  // 基于结构化程度调整
  const hasSections = content.includes('#');
  if (hasSections) confidence += 0.1;
  
  return Math.min(0.95, confidence);
}

/**
 * 格式化内容为HTML
 */
export function formatContent(content: string, type: AnswerSection['type']): string {
  let formatted = content;
  
  switch (type) {
    case 'code':
      formatted = formatCodeBlock(formatted);
      break;
    case 'list':
      formatted = formatList(formatted);
      break;
    case 'table':
      formatted = formatTable(formatted);
      break;
    case 'quote':
      formatted = formatQuote(formatted);
      break;
    default:
      formatted = formatText(formatted);
  }
  
  return formatted;
}

function formatInline(content: string): string {
  // 按顺序处理：先粗体，再斜体，最后代码
  // 1. 处理粗体 **text**（两个星号，优先处理）
  let result = content.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
  
  // 2. 处理斜体 *text*（单个星号，粗体已替换所以不会冲突）
  result = result.replace(/\*([^*\n]+?)\*/g, '<em>$1</em>');
  
  // 3. 处理行内代码 `code`
  result = result.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  return result;
}

/**
 * 格式化代码块
 */
function formatCodeBlock(content: string): string {
  return content
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
}

/**
 * 格式化列表
 */
function formatList(content: string): string {
  const lines = content.split('\n')
  let html = ''
  let inUl = false
  let inOl = false
  let currentListItem = ''

  const closeLists = () => {
    if (currentListItem) {
      // 处理当前列表项的剩余内容
      if (inUl) {
        html += `<li>${formatInline(currentListItem.trim())}</li>`
      } else if (inOl) {
        html += `<li>${formatInline(currentListItem.trim())}</li>`
      }
      currentListItem = ''
    }
    if (inUl) {
      html += '</ul>'
      inUl = false
    }
    if (inOl) {
      html += '</ol>'
      inOl = false
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()
    const isIndented = rawLine.match(/^\s{2,}/) // 检测缩进（2个或更多空格）
    
    if (/^[-*+]\s+/.test(line)) {
      // 如果有未完成的列表项，先关闭它
      if (currentListItem) {
        if (inUl) {
          html += `<li>${formatInline(currentListItem.trim())}</li>`
        } else if (inOl) {
          html += `<li>${formatInline(currentListItem.trim())}</li>`
        }
        currentListItem = ''
      }
      
      if (!inUl) {
        closeLists()
        html += '<ul>'
        inUl = true
      }
      currentListItem = line.replace(/^[-*+]\s+/, '')
    } else if (/^\d+\.\s+/.test(line)) {
      // 如果有未完成的列表项，先关闭它
      if (currentListItem) {
        if (inUl) {
          html += `<li>${formatInline(currentListItem.trim())}</li>`
        } else if (inOl) {
          html += `<li>${formatInline(currentListItem.trim())}</li>`
        }
        currentListItem = ''
      }
      
      if (!inOl) {
        closeLists()
        html += '<ol>'
        inOl = true
      }
      currentListItem = line.replace(/^\d+\.\s+/, '')
    } else if (isIndented && (inUl || inOl) && currentListItem) {
      // 缩进的行是当前列表项的延续
      currentListItem += ' ' + line
    } else if (line) {
      // 如果有未完成的列表项，先关闭它
      if (currentListItem) {
        if (inUl) {
          html += `<li>${formatInline(currentListItem.trim())}</li>`
        } else if (inOl) {
          html += `<li>${formatInline(currentListItem.trim())}</li>`
        }
        currentListItem = ''
      }
      closeLists()
      html += `<p>${formatInline(line)}</p>`
    }
  }

  // 处理最后一个列表项
  if (currentListItem) {
    if (inUl) {
      html += `<li>${formatInline(currentListItem.trim())}</li>`
    } else if (inOl) {
      html += `<li>${formatInline(currentListItem.trim())}</li>`
    }
  }

  closeLists()
  return html || formatText(content)
}

/**
 * 格式化表格
 */
function formatTable(content: string): string {
  const lines = content.split('\n');
  let tableHtml = '<table class="answer-table">';
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line.includes('|')) {
      if (i === 0) {
        // 表头
        const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
        tableHtml += '<thead><tr>';
        cells.forEach(cell => {
          tableHtml += `<th>${cell}</th>`;
        });
        tableHtml += '</tr></thead>';
      } else if (line.includes('---')) {
        // 分隔线，跳过
        continue;
      } else {
        // 数据行
        const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
        if (cells.length > 0) {
          tableHtml += '<tr>';
          cells.forEach(cell => {
            tableHtml += `<td>${cell}</td>`;
          });
          tableHtml += '</tr>';
        }
      }
    }
  }
  
  tableHtml += '</table>';
  return tableHtml;
}

/**
 * 格式化引用
 */
function formatQuote(content: string): string {
  return content.replace(/^>\s*(.+)$/gm, (_match, text) => `<blockquote>${formatInline(text)}</blockquote>`);
}

/**
 * 格式化普通文本
 */
function formatText(content: string): string {
  // 先按段落分割，然后格式化每个段落
  const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim())
  
  if (paragraphs.length === 0) {
    return formatInline(content).replace(/\n/g, '<br>')
  }
  
  // 格式化每个段落，保持换行
  return paragraphs.map(para => {
    const formatted = formatInline(para.trim())
    // 段落内的单个换行转换为 <br>
    return `<p>${formatted.replace(/\n/g, '<br>')}</p>`
  }).join('')
}
