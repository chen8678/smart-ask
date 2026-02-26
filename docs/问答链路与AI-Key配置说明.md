# 问答链路与 AI Key 配置说明

## 1. 问答用的是什么链路？还是之前的 RAG 吗？

**是的，仍然是之前的 RAG（检索增强生成）链路。**

### 1.1 调用关系

```
用户提问
    ↓
QAService.ask_question()          （apps/chat/services.py）
    ↓
RAGRetrievalService.search_documents()   ← 使用 RAG 检索
    ↓
HybridRetrievalService.search_documents() （apps/knowledge/vectorization_service.py）
    ├─ 主路径：VectorRetrievalService（向量检索，依赖 VectorizationService）
    └─ 无结果时：回退到关键词检索（_fallback_keyword_search）
    ↓
取 Top-K 文档，拼成「知识库上下文」
    ↓
AIServiceFactory 创建的 AI 服务（DeepSeek/Qwen/GLM）生成答案
    ↓
返回 answer + sources
```

### 1.2 各环节说明

| 环节 | 说明 |
|------|------|
| **检索** | RAGRetrievalService → HybridRetrievalService：先做**向量检索**，没有结果时用**关键词检索**。 |
| **向量化** | VectorizationService：可连**向量化微服务**（如 `VECTORIZATION_SERVICE_URL`），连不上时用项目内 **TF-IDF 降级**。 |
| **生成** | 用「问题 + 知识库上下文」调 **大模型 API**（DeepSeek/通义千问/智谱等）生成答案。 |

所以：**问答 = 之前的 RAG：检索（向量/关键词）→ 拼上下文 → 大模型生成。**

---

## 2. AI Key 是后端配备还是要自己配备？

**两种方式都支持：后端统一配备 或 自己在系统里配备。**

### 2.1 后端配备（推荐部署/演示用）

**方式 A：环境变量**

在运行后端的机器上配置环境变量，例如：

```bash
export DEEPSEEK_API_KEY=sk-xxx    # DeepSeek（当前默认模型）
export QWEN_API_KEY=sk-xxx        # 通义千问（可选）
export GLM_API_KEY=xxx            # 智谱（可选）
```

或在 `backend/.env` 里写：

```
DEEPSEEK_API_KEY=sk-xxx
QWEN_API_KEY=sk-xxx
GLM_API_KEY=xxx
```

**方式 B：在 settings.py 里写死（仅适合测试）**

当前 `ai_qa_system/settings.py` 里有：

```python
AI_ENGINE_CONFIG = {
    'deepseek': {
        'api_key': 'sk-edd63afd81c640a89abc4c77bf5df472',  # 临时硬编码测试
        ...
    },
    'qwen': {
        'api_key': os.getenv('QWEN_API_KEY', ''),
        ...
    },
    'glm': {
        'api_key': os.getenv('GLM_API_KEY', ''),
        ...
    }
}
```

- **deepseek**：这里写死的 key 会优先生效（生产环境建议改成用环境变量）。
- **qwen / glm**：未在 settings 里写死，只能通过环境变量或下面「自己配备」的方式生效。

**取 Key 顺序（QAService 里）**  
1. 先看 `settings.AI_ENGINE_CONFIG[provider]['api_key']`  
2. 若为空，再读环境变量 `DEEPSEEK_API_KEY` / `QWEN_API_KEY` / `GLM_API_KEY`

所以：**后端配备 = 改环境变量或改 settings 里的 AI_ENGINE_CONFIG。**

### 2.2 自己配备（通过系统界面/数据库）

- 使用**带登录的完整前端**时，可以进 **「AI 模型配置」** 页面（如 `/ai-models`）填写各厂商的 API Key 并保存。
- 保存后会写入数据库表 **APIKeyConfig**；部分逻辑（如学习、引擎工厂）会优先读数据库里的 Key。
- **简单版免登录页**（`/` 的 AppSimple）**没有**配置入口，用的完全是**后端配备**的 Key（环境变量或 settings）。

总结：

- **只做演示/内网部署**：在后端用**环境变量**（或 settings）配好 `DEEPSEEK_API_KEY` 等即可，无需自己再在界面配。
- **希望用户在系统里自己填 Key**：用完整版前端登录后，在「AI 模型配置」里配备；简单版页面的问答仍然依赖后端已配好的 Key。

---

## 3. 小结

| 问题 | 答案 |
|------|------|
| 问答链路还是 RAG 吗？ | **是**。检索（向量 + 关键词回退）→ 拼上下文 → 大模型生成。 |
| AI Key 谁配？ | **后端配**：环境变量或 `settings.AI_ENGINE_CONFIG`；**自己配**：完整版前端的「AI 模型配置」页面（写入数据库）。简单版页面只用后端配的 Key。 |
