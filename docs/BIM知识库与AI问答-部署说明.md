# BIM 知识库 + AI 问答 · 简单版部署说明

## 功能概览

- **知识库**：创建知识库，上传 BIM 数据（.json / .ifc）
- **BIM → JSON 入库**：上传 .json 或 .ifc 后自动转为统一 JSON 并入库、向量化
- **AI 问答**：基于知识库的 RAG 问答（简单查询接口）

## 一、BIM 数据 → JSON → 入库

### 1.1 支持格式

| 格式 | 说明 | 依赖 |
|------|------|------|
| **.json** | BIM 工具导出的 JSON | 无，直接解析入库 |
| **.ifc** | IFC 模型文件 | 需安装 `ifcopenshell` |

### 1.2 流程

```
BIM 文件 (.json / .ifc)
    → bim_processor.bim_to_json() 转为统一 JSON
    → 可检索文本写入 Document.content，完整 JSON 写入 metadata
    → VectorizationService 向量化 content
    → 入库完成，可被 RAG 检索
```

### 1.3 接口

- **上传 BIM**：`POST /api/v1/knowledge/<knowledge_base_id>/bim/`
  - Content-Type: `multipart/form-data`
  - 字段：`file`（.json 或 .ifc，建议 ≤50MB）

### 1.4 IFC 支持（可选）

若需支持 .ifc 上传，在 backend 环境安装：

```bash
pip install ifcopenshell
```

未安装时上传 .ifc 会返回错误，提示安装或改为上传 .json。

## 二、本地运行（开发/演示）

### 2.1 环境

- Python 3.9+
- Node.js 18+
- PostgreSQL 15 + pgvector（或使用 Docker 中的 postgres）
- Redis（可选，部分功能用）
- 向量化：项目内 VectorizationService（可连向量化微服务或走 TF-IDF 降级）

### 2.2 后端

```bash
cd chen-AI/backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# 可选：pip install ifcopenshell

# 配置环境变量（或 .env）
export DATABASE_URL=postgresql://user:pass@localhost:5432/chen_ai
export SECRET_KEY=your-secret-key
export DEEPSEEK_API_KEY=your-api-key   # 问答用

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 2.3 前端

```bash
cd chen-AI/frontend
npm install
npm run dev
```

### 2.4 使用

1. 打开 `http://localhost:3000/bim-qa`，登录。
2. **知识库 / BIM 上传**：创建知识库 → 选择知识库 → 上传 .json 或 .ifc。
3. **AI 问答**：选择知识库 → 输入问题 → 提问。

## 三、Docker 部署

### 3.1 使用现有 docker-compose

项目根目录已有 `docker-compose.yml`，包含 backend、frontend、postgres、redis、vectorization 等：

```bash
cd chen-AI
docker-compose up -d
```

- 后端：http://localhost:8000  
- 前端：http://localhost:3000  
- 访问 `/bim-qa` 使用 BIM 知识库与问答。

### 3.2 仅部署“简单版”后端 + 数据库（可选）

若只需 API + 数据库，可只起 backend 与 postgres（前端用现有或单独构建）：

```yaml
# docker-compose.simple.yml 示例
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: chen_ai
      POSTGRES_USER: chen_ai
      POSTGRES_PASSWORD: your_password
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://chen_ai:your_password@postgres:5432/chen_ai
      SECRET_KEY: your-secret-key
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}

volumes:
  postgres_data:
```

```bash
docker-compose -f docker-compose.simple.yml up -d
```

### 3.3 镜像构建与 ifcopenshell（可选）

若要在 Docker 中支持 .ifc，在 `backend/Dockerfile` 中增加：

```dockerfile
RUN pip install ifcopenshell
```

或多阶段构建时在运行镜像中 `pip install ifcopenshell`。

## 四、代码结构（与本功能相关）

| 路径 | 说明 |
|------|------|
| `backend/apps/knowledge/bim_processor.py` | BIM/IFC → 统一 JSON，可检索文本生成 |
| `backend/apps/knowledge/views.py` | `upload_bim` 视图：接收文件、调 bim_processor、入库与向量化 |
| `backend/apps/knowledge/urls.py` | `<kb_id>/bim/` 路由 |
| `backend/apps/chat/simple_query.py` | 简单问答接口，基于知识库 RAG |
| `frontend/src/views/BIMKnowledgeQA.vue` | 知识库 + BIM 上传 + AI 问答页 |
| `frontend/src/router/index.ts` | `/bim-qa` 路由 |

## 五、环境变量摘要

| 变量 | 必填 | 说明 |
|------|------|------|
| `DATABASE_URL` | 是 | PostgreSQL 连接串（含 pgvector） |
| `SECRET_KEY` | 是 | Django 密钥 |
| `DEEPSEEK_API_KEY` | 问答 | 简单问答使用的模型 API Key |
| `REDIS_URL` | 部分功能 | Celery/缓存等 |
| 向量化微服务 | 可选 | 不配置时使用 TF-IDF 降级 |

## 六、常见问题

1. **上传 .ifc 报错“需要安装 ifcopenshell”**  
   在 backend 环境中执行：`pip install ifcopenshell`，或改为上传 BIM 导出的 .json。

2. **问答无结果或不准**  
   确认知识库中已有文档且已向量化；若未连向量化微服务，会走 TF-IDF，效果会弱于向量检索。

3. **前端请求 404**  
   确认后端已起在 8000，且前端请求的 baseURL 为 `/api/v1`（或对应代理到后端）。

4. **CORS 报错**  
   在 Django 中配置 `CORS_ALLOWED_ORIGINS` 包含前端地址（如 `http://localhost:3000`）。
