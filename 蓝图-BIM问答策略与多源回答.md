# chen-AI-测试包 · BIM 问答策略与多源回答 蓝图

> 基于当前项目分析与前述建议制定，目标：**一、BIM 数据准确引用；二、问题正常回答（不轻易“无法得到答案”）**。

---

## 一、项目现状简要分析

### 1.1 架构与数据流

| 环节 | 现状 | 说明 |
|------|------|------|
| **前端** | `Chat.vue` 调用 `POST /chat/ask/`，可选知识库、模型；另有「策略/证据面板」调用 `POST /knowledge/preview-retrieval/` | 预览检索与真实问答**未打通**：问答未使用预览时的策略参数 |
| **问答入口** | `apps/chat/views.py` → `QAService.ask_question()` | 单知识库、无 strategy/top_k 等参数 |
| **检索** | `QAService` 使用 `RAGRetrievalService` → `HybridRetrievalService`（向量 + 关键词回退） | 与 `AdvancedRetrievalService` / `RetrievalStrategyManager` **分离**，问答未用 pgvector+BM25 混合策略 |
| **上下文构建** | `generate_answer()` 中 `context = 文档标题 + content[:500]` | 未区分 BIM 与普通文档；未注入「当前 BIM 含哪些 Ifc 类型」等结构化说明 |
| **无检索结果时** | 使用 `prompts.get_no_context_prompts(question)` | 提示词要求「说明未检索到匹配内容并给出建议」→ 易变成**直接拒答**，不做业务兜底 |

### 1.2 问题根因归纳

1. **BIM 引用不足**：有检索结果时，提示词未要求「先概括当前 BIM 文档中的元素类型/名称」，也未区分「来自 BIM」与「来自规范/标准」。
2. **拒答逻辑过重**：无检索结果时仅走「无上下文」分支，不允许模型用通用规范/经验做**兜底回答**，且未区分「BIM 中无此数据」与「应给出规范建议」。
3. **知识源单一**：当前仅支持单知识库检索，无法在同一轮问答中同时检索「BIM 模型库」与「安全/规范文档库」并合并上下文。
4. **检索与问答脱节**：前端策略面板的 hybrid/vector_only/bm25_only 及 top_k、阈值仅用于预览，`/chat/ask/` 未使用，问答检索路径与预览不一致。

---

## 二、目标行为（期望效果）

- **BIM 数据准确引用**  
  - 每次回答中，若用到了 BIM 文档，需明确写出：来源文件名、所含 Ifc 类型及名称（如 `IfcDoor / StandardDoor`）。  
  - 若问题涉及的内容（如塔吊、安全距离）**不在**当前 BIM 中，也需明确说明「当前 BIM 未包含……」，避免用户误以为模型里有塔吊数据。

- **问题正常回答**  
  - 对于「塔吊作业半径内安全防护距离的公司统一标准」类问题：即使用户当前只选了「仅含门墙窗」的 IFC 知识库，也应给出**基于规范/经验的兜底回答**（如安全距离建议、警戒范围等），并在回答中说明：  
    - 该结论**不是**来自当前 BIM 模型；  
    - 来自公司标准/行业规范或通用工程经验（若知识库有规范文档则引用文档）。

- **回答结构统一（三段式）**  
  1. **BIM/文档数据情况**：当前检索到的 BIM 或文档包含/不包含哪些与问题相关的内容；  
  2. **基于标准/规范的具体回答**：可直接采用的要点（数值、流程、注意事项）；  
  3. **数据来源与局限性**：哪些来自 BIM、哪些来自规范/经验，以及后续如何用 BIM 落地（如施工阶段建模塔吊与安全区域）。

---

## 三、蓝图：分阶段改造

### 阶段一：提示词与「无上下文」策略（优先、低成本）

**目标**：不增加新知识库、不改检索架构的前提下，先实现「BIM 准确引用 + 兜底回答 + 三段式结构」。

| 项 | 内容 |
|----|------|
| **1. 修改无上下文提示词** | 在 `apps/chat/prompts.py` 中调整 `PROMPT_NO_CONTEXT_*`：<br>• 删除或弱化「仅说明未检索到并建议上传」的单一行为。<br>• 改为：若问题属于智慧工地/施工安全/BIM 等**领域内**，则**先简短说明**当前知识库未检索到可直接引用的内容，再**允许**基于通用规范/工程经验给出**保守、可操作的兜底回答**，并注明「以下为通用规范/经验建议，非当前知识库内容」。 |
| **2. 新增「BIM + 兜底」专用提示词** | 增加一组 prompt（如 `get_rag_with_bim_scope_prompts`）：<br>• 当检索结果中**包含** BIM 文档（`metadata.source == 'bim'`）时使用。<br>• **System**：要求先概括「当前 BIM 上下文」：来源文件、Ifc 类型与名称列表；若问题涉及的对象（如塔吊）不在这些类型中，必须明确写「当前 BIM 未包含…」；再基于规范/知识库/经验给出业务回答；最后用 1～2 句区分「来自 BIM / 来自规范或经验」。<br>• **User**：注入「BIM 元素摘要」+ 原始 context + 问题。 |
| **3. 回答结构约束** | 在 RAG 与「无上下文」的 system 中统一增加：<br>• 回答须包含（若适用）：① BIM/文档数据情况 ② 具体答案要点 ③ 来源与局限性说明。<br>• 禁止在领域内问题上**仅**输出「无法从当前 BIM/知识库得到答案」即结束；须至少给出简短规范/经验建议并标注来源。 |

**涉及文件**：`backend/apps/chat/prompts.py`，`backend/apps/chat/services.py`（在 `generate_answer` 中根据 `context_docs` 是否含 BIM 选择不同 prompt，无结果时用新的无上下文逻辑）。

---

### 阶段二：问答检索与策略统一

**目标**：让 `/chat/ask/` 使用与「策略/证据面板」一致的检索能力，并支持可选策略参数。

| 项 | 内容 |
|----|------|
| **1. 问答检索改用 AdvancedRetrievalService** | 在 `QAService.ask_question()` 中：<br>• 改为调用 `RetrievalStrategyManager().execute_strategy(...)`（或直接使用 `AdvancedRetrievalService.hybrid_search`），传入当前选中的知识库 ID、以及可配置的 strategy / top_k / score_threshold / alpha。<br>• 从返回的 `evidence` 中取 `source.document_id`，再查询 `Document` 得到 `context_docs`，用于构建上下文。 |
| **2. 请求参数扩展** | `POST /chat/ask/` 增加可选参数：`strategy`, `top_k`, `score_threshold`, `alpha`（与 preview-retrieval 一致）。前端在发送时可从「策略面板」的当前配置读取并传入（可选，默认与现有一致）。 |
| **3. 上下文构建增强** | 构建 context 时：<br>• 若文档 `metadata.get('source') == 'bim'`，除 content 外，可拼接一段「BIM 元素摘要」（从 content 或 metadata 解析 type/name 列表），便于模型先写「BIM 数据情况」再回答。 |

**涉及文件**：`backend/apps/chat/services.py`（QAService）、`backend/apps/chat/views.py`（ask 参数）、前端 `Chat.vue`（可选：传策略参数）。

---

### 阶段三：知识库拆分与多源检索（可选）

**目标**：支持「BIM 库 + 安全/规范库」同时参与检索，从源头区分 BIM 与规范类知识。

| 项 | 内容 |
|----|------|
| **1. 知识库角色** | • 建议至少两个知识库：**BIM 模型库**（仅放 IFC/JSON）、**安全/规范文档库**（公司制度、塔吊安全标准等 PDF/Word）。<br>• 或：单知识库内通过文档 `metadata` 标记 `source: 'bim'` 与 `source: 'standard'`，检索后分组注入 prompt。 |
| **2. 多源检索** | • 方案 A：前端允许选择「主知识库 + 辅助知识库」，后端对两库分别检索后合并 evidence，再按「BIM 块 / 规范块」组织 context。<br>• 方案 B：单知识库内按 metadata 过滤，先取 BIM 文档、再取非 BIM 文档，合并后统一注入，并在 prompt 中说明「以下分为 BIM 上下文与规范/标准上下文」。 |
| **3. 提示词** | 使用阶段一已实现的「BIM + 规范」分段格式，在 system 中明确：先写 BIM 能/不能回答什么，再写规范/标准中的答案，最后写来源与局限。 |

**涉及文件**：`backend/apps/chat/services.py`、`backend/apps/knowledge/retrieval_service.py`（若支持多 KB）、前端知识库选择与策略面板。

---

### 阶段四：BIM 结构化摘要（增强引用质量）

**目标**：让「BIM 数据情况」更准确、可读。

| 项 | 内容 |
|----|------|
| **1. 入库时保留元素列表** | 在 `upload_bim` 中，将 `elements` 的 type/name 列表写入 `metadata.bim_elements`（或已在 `bim_json_to_searchable_text` 中生成的可解析摘要），便于检索后直接注入 prompt，无需再解析长 content。 |
| **2. 检索结果中附带 BIM 摘要** | 若 evidence 来自 BIM 文档，在构建 context 时优先使用 `metadata.bim_elements` 或从 content 首段提取的「BIM来源: … 格式: … type: …」行，形成简短「BIM 元素清单」块，再拼入全文 context。 |

**涉及文件**：`backend/apps/knowledge/bim_processor.py`、`backend/apps/knowledge/views.py`（upload_bim）、`backend/apps/chat/services.py`（上下文构建）。

---

## 四、实施优先级与依赖

| 优先级 | 阶段 | 依赖 | 预期效果 |
|--------|------|------|----------|
| **P0** | 阶段一 | 无 | 立刻改善：无检索结果时也有兜底回答；有 BIM 时可要求先写 BIM 情况再回答；统一三段式结构。 |
| **P1** | 阶段二 | 无 | 问答与预览检索一致；可调 top_k/阈值，减少误拒答。 |
| **P2** | 阶段三 | 阶段一 | 规范类问题可同时命中 BIM + 公司标准文档，回答更可引用。 |
| **P3** | 阶段四 | 阶段一、二 | BIM 引用更精确，便于用户核对。 |

---

## 五、验收标准（示例）

- **BIM 引用**：对「单扇标准门窗组合 IFC 测试模型」知识库提问「塔吊作业半径内安全防护距离」时，回答中应出现：  
  - 当前 BIM 包含 IfcDoor、IfcWallStandardCase、IfcWindow 等，**不包含**塔吊或安全距离数据；  
  - 并给出安全防护距离/警戒范围的**具体建议**（来自规范或经验），并注明非来自该 BIM。
- **正常回答**：同一问题**不应**仅输出「无法从当前 BIM 上下文中得到答案」即结束；须至少有 1～2 段可操作的规范/经验建议。
- **结构**：回答中能区分「BIM/文档情况」「具体答案」「来源与局限」三部分（可为段落形式，不必强制小标题）。

---

## 六、附录：当前关键代码位置

| 功能 | 文件路径 |
|------|----------|
| 问答入口 | `backend/apps/chat/views.py` → `ask_question` |
| 检索与生成 | `backend/apps/chat/services.py` → `QAService.ask_question`, `generate_answer` |
| 无上下文/ RAG 提示词 | `backend/apps/chat/prompts.py` → `get_no_context_prompts`, `get_rag_prompts` |
| 预览检索（策略面板） | `backend/apps/knowledge/views.py` → `preview_retrieval` |
| 高级检索与策略 | `backend/apps/knowledge/retrieval_service.py` → `AdvancedRetrievalService`, `RetrievalStrategyManager` |
| BIM 上传与文本化 | `backend/apps/knowledge/views.py` → `upload_bim`；`backend/apps/knowledge/bim_processor.py` → `bim_to_json`, `bim_json_to_searchable_text` |
| 前端聊天与策略 | `chen-AI-测试包/frontend/src/views/Chat.vue` |

---

*文档版本：v1 | 基于 chen-AI-测试包 项目分析及「BIM 准确引用 + 问题正常回答」需求整理。*
