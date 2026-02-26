# Apple 黑白 + 炫彩 QA 检查表（阶段性审查 2025-11-17）

## 通用基线
| 检查项 | 说明 | 现状 | 结论 |
| --- | --- | --- | --- |
| **B/W 基底** | 大面积黑/白或浅灰背景，搭配柔和阴影 | `App.vue` 变量已统一（`--apple-background` 等） | ✅ |
| **炫彩点缀** | 使用 SF Symbols 线性图标 + 渐变按钮/标签 | 主要模块已引用 AppleIcon，部分老按钮仍保留 Element 色块 | ⚠️ |
| **SF Pro 字体** | 通过 `fonts.css` + `App.vue` 全局启用 | 全站继承 | ✅ |
| **Ghost Button 模式** | 低强调操作应使用 `ghost-btn` | 局部（Learning/AIConfig）完成，Chat/KnowledgeBase 仍使用彩色圆角按钮 | ⚠️ |
| **图表主题** | ECharts 读取 `:root` 变量，线条/填充协调 | `RadarChart`、`ProgressChart` 已调和 | ✅ |

---

## 逐页审查

### 1. Chat (`src/views/Chat.vue`)
| 检查项 | 现状 | 结论 / 后续 |
| --- | --- | --- |
| 顶部黑白基底 | `chat-container` 背景为浅灰，符合 HIG | ✅ |
| 炫彩点缀 | header icon 使用 AppleIcon，但 header-actions 仍是 `type="warning/success"` 彩块 | ⚠️ 建议改为 ghost 或描边按钮 |
| 输入区 | Textarea 样式保持 Element 默认（方正+投影） | ⚠️ 继承 `ghost`/`glass` 风格，添加柔和阴影 |
| 空态 | 使用 `el-icon`，未替换为 AppleIcon | ⚠️ 替换 `ChatDotRound` 为 SF Symbol |
| 响应式 | 已有媒体查询，移动端 header stack 正常 | ✅ |

### 2. KnowledgeBase (`src/views/KnowledgeBase.vue`)
| 检查项 | 现状 | 结论 / 后续 |
| --- | --- | --- |
| 背景/分区 | header + main 仍为 Element 白底 + 直角卡片 | ⚠️ 需要引入玻璃壳 & 加大圆角 |
| 操作按钮 | 大量 `type="primary/success"` 传统按钮 | ⚠️ 改用 ghost / Apple 渐变 |
| 卡片信息 | AppleIcon 已使用，标签颜色为 Element 默认 | ⚠️ 使用自定义 `:style`，避免彩色填充块 |
| Modal | 继承全局变量即可，视觉 OK | ✅ |

### 3. FinancialCompliance (`src/views/FinancialCompliance.vue`)
| 检查项 | 现状 | 结论 |
| --- | --- | --- |
| 黑白基底 + 彩色条 | 已实现 intro + column-card 渐变 | ✅ |
| 控件 | filter bar 使用描边输入、时间选择器对齐 | ✅ |
| 结果面板 | 使用 `risk-low/medium/high` 纯色文字，建议配合渐变条 | ⚠️（低优先） |

### 4. MedicalAssistant (`src/views/MedicalAssistant.vue`)
| 检查项 | 现状 | 结论 |
| --- | --- | --- |
| 双列布局 | Column card 具备渐变顶条，符合 Apple 风格 | ✅ |
| 快捷 pill | 已采用圆角 + rgba hover | ✅ |
| 药品列表 | 仍为直角分隔线，颜色偏浅 | ⚠️ 可加浅阴影+背景 |

### 5. LearningAnalytics (`src/views/LearningAnalytics.vue`)
| 检查项 | 现状 | 结论 |
| --- | --- | --- |
| 顶部导航 | 已是 `AppleIcon` + ghost buttons | ✅ |
| 图表 | Progress/Radar/MindMap now读变量 | ✅ |
| 子卡片 | 少量 Element 默认按钮（`el-button type="text"`）需更换 | ⚠️ |

### 6. Industry 双列（金融/医疗）
- 与上方 3/4 重复，此处只记录截图建议：金融时间轴 + 医疗诊断在 MacBook Bezel 里左右排布，间距 48px，可展示黑白+彩色对比。

---

## 输出物：Bezel 物料
| 文件 | 用途 |
| --- | --- |
| `src/design/bezel-kit.md` | 已整理画布、分层、导出步骤，可直接在 Figma 使用 |

---

## 后续建议
1. **Chat & KnowledgeBase**：批量改造按钮/输入，复用 `.ghost-btn`、`.control-select` 类；空态图标改用 AppleIcon。
2. **医疗药品列表**：调成玻璃卡 or 轻阴影，避免默认分隔线。
3. **LearningAnalytics**：把 `el-button type="text"` 调整为自定义描边按钮，保持一致视觉节奏。

> 完成以上整改后，可再次依据本表逐页打勾，并更新截图供竞赛材料使用。 

