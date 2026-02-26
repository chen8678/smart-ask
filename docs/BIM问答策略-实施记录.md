# BIM 问答策略 · 分阶段实施记录

> 按 `蓝图-BIM问答策略与多源回答.md` 逐阶段实现并记录、检查。

---

## 阶段一：提示词与「无上下文」策略 ✅

**状态**：已完成（此前会话已实现）

**实现内容**：
1. **无上下文提示词**（`prompts.py`）：重写 `PROMPT_NO_CONTEXT_*`，领域内允许兜底回答并注明「非当前知识库内容」，禁止仅拒答。
2. **RAG 三段式**：在 `PROMPT_RAG_SYSTEM` 中增加 ① BIM/文档情况 ② 具体答案 ③ 来源与局限；禁止领域内仅输出「无法得到答案」。
3. **BIM 专用 prompt**：新增 `PROMPT_RAG_BIM_*` 与 `get_rag_with_bim_scope_prompts(question, context, bim_summary)`。
4. **services.py**：无结果时用新无上下文逻辑；有结果时若存在 `metadata.source == 'bim'` 则拼 `bim_summary` 并走 BIM 专用 prompt。

**涉及文件**：`backend/apps/chat/prompts.py`，`backend/apps/chat/services.py`

**检查**：
- [x] 无上下文提示词包含「领域内须给出兜底回答」
- [x] RAG 提示词包含三段式及禁止仅拒答
- [x] 存在 `get_rag_with_bim_scope_prompts` 且接受 `bim_summary`
- [x] `generate_answer` 中根据 BIM 文档分支并传入 `bim_summary`

---

## 阶段二：问答检索与策略统一 ✅

**状态**：已完成

**实现内容**：
1. **QAService**（`services.py`）：新增 `_retrieve_with_strategy(question, knowledge_base_id, strategy, top_k, score_threshold, alpha)`，内部调用 `RetrievalStrategyManager().execute_strategy(...)`，从 `evidence` 解析 `document_id` 并查 `Document` 得到有序 `context_docs`；异常时回退到 `RAGRetrievalService.search_documents`。
2. **ask_question**：接受 `retrieval_params`（strategy, top_k, score_threshold, alpha），始终使用 `_retrieve_with_strategy` 做检索（带默认参数）。
3. **views.py**：`POST /chat/ask/` 从 `request.data` 读取可选 `strategy`, `top_k`, `score_threshold`, `alpha`，做安全类型转换后传入 `qa_service.ask_question(..., retrieval_params=...)`。
4. **前端**：`Chat.vue` 在发送 `/chat/ask/` 时已携带 `strategy`, `top_k`, `score_threshold`, `alpha`（与策略面板一致）。

**涉及文件**：`backend/apps/chat/services.py`，`backend/apps/chat/views.py`，`frontend/src/views/Chat.vue`

**检查**：
- [x] 问答使用 `RetrievalStrategyManager` / 高级检索，与预览一致
- [x] 请求支持 strategy / top_k / score_threshold / alpha
- [x] 高级检索失败时回退到原混合检索
- [x] 前端请求体包含策略参数

---

## 阶段三：知识库多源检索（主 + 辅）✅

**状态**：已完成

**实现内容**：
1. **QAService**：新增 `_retrieve_multi_kb(question, main_kb_id, auxiliary_kb_ids, user, strategy, top_k, score_threshold, alpha)`。主库检索 `main_per_k` 条（约 top_k - 辅助数*2），各辅助库检索 2 条；仅对用户有权限的 `KnowledgeBase` 做辅助检索；按 score 合并、按 document_id 去重后取前 top_k，再解析为 Document 列表。
2. **ask_question**：接受可选 `auxiliary_knowledge_base_ids: List[str]`；若提供则走 `_retrieve_multi_kb`，否则走 `_retrieve_with_strategy`。
3. **views.py**：从 `request.data` 读取可选 `auxiliary_knowledge_base_ids`（list），校验为列表后传入 `ask_question`。辅助库权限在 `_retrieve_multi_kb` 内按 `KnowledgeBase.objects.filter(owner=user, id__in=...)` 校验。

**涉及文件**：`backend/apps/chat/services.py`，`backend/apps/chat/views.py`

**检查**：
- [x] 支持主库 + 辅助库 ID 列表
- [x] 辅助库仅检索当前用户拥有的知识库
- [x] 多库结果按分数合并、按 document_id 去重
- [ ] 前端多选辅助知识库（可选，API 已支持，前端可后续增加）

---

## 阶段四：BIM 结构化摘要（metadata.bim_elements）✅

**状态**：已完成

**实现内容**：
1. **bim_processor.py**：新增 `bim_json_to_elements_list(bim_json)`，从 `elements`/`items` 提取每项 `type`/`name`，返回 `List[Dict]`，便于序列化存入 metadata。
2. **upload_bim**（`views.py`）：在 `safe_meta` 中增加 `bim_elements`，取 `_ensure_json_serializable(bim_json_to_elements_list(bim_json))`；入库时写入 `Document.metadata`。
3. **generate_answer**（`services.py`）：构建 `bim_summary` 时，若 `doc.metadata.get('bim_elements')` 存在且为列表，则用其格式化为「type: X | name: Y」行（最多 80 条），不再截断 content 前 1200 字；否则仍用 content 首段。

**涉及文件**：`backend/apps/knowledge/bim_processor.py`，`backend/apps/knowledge/views.py`，`backend/apps/chat/services.py`

**检查**：
- [x] 新上传 BIM 文档的 metadata 含 `bim_elements`
- [x] 检索到 BIM 文档时优先用 `metadata.bim_elements` 生成摘要
- [x] 旧文档无 `bim_elements` 时仍用 content 首段

---

## 总结

| 阶段 | 状态 | 说明 |
|------|------|------|
| 一 | ✅ | 提示词与无上下文兜底、BIM 专用 prompt、三段式 |
| 二 | ✅ | 问答检索统一为高级检索，支持策略参数，前端已传参 |
| 三 | ✅ | 主库 + 辅助库多源检索，权限校验，API 就绪 |
| 四 | ✅ | BIM 入库写 bim_elements，生成答案优先用 bim_elements 摘要 |

**说明**：阶段三的前端「辅助知识库」多选 UI 未实现，调用方可直接在请求体中传 `auxiliary_knowledge_base_ids: [uuid1, uuid2]` 使用多源检索。

---

*文档版本：v1 | 与蓝图四阶段实现同步。*
