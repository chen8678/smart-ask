# 从 GitHub 拉取项目到本地并部署使用手册

本文档说明如何从 GitHub 仓库 **smart-ask** 将「BIM 智慧工地问答」项目克隆到本地，完成环境配置与启动，并正常使用。

---

## 一、前置环境要求

| 项目 | 版本要求 | 说明 |
|------|----------|------|
| **Git** | 2.x | 用于克隆仓库 |
| **Python** | 3.9+ | 后端运行环境 |
| **Node.js** | 18+ | 前端构建与开发 |
| **PostgreSQL** | 12+ | 数据库，需支持 **pgvector** 扩展 |
| **npm** | 随 Node 安装 | 前端依赖安装 |

- **macOS**：可用 Homebrew 安装：`brew install postgresql@14 node python@3.9`，pgvector 需单独安装或使用带 pgvector 的 Postgres 发行版。
- **Windows**：可安装 [PostgreSQL 官方安装包](https://www.postgresql.org/download/windows/)，并安装 [pgvector 扩展](https://github.com/pgvector/pgvector#installation)。

---

## 二、从 GitHub 克隆项目

### 方式一：SSH（推荐，需已配置 SSH 公钥）

```bash
git clone git@github.com:chen8678/smart-ask.git
cd smart-ask
```

### 方式二：HTTPS

```bash
git clone https://github.com/chen8678/smart-ask.git
cd smart-ask
```

克隆完成后，当前目录即为项目根目录（即原「chen-AI-测试包」内容）。

---

## 三、数据库准备

1. **启动 PostgreSQL 服务**（若未自动启动）  
   - macOS：`brew services start postgresql@14` 或根据你的安装方式启动。  
   - Windows：在「服务」中启动 PostgreSQL。

2. **创建数据库并启用 pgvector**  
   使用 `psql` 或 pgAdmin 等工具连接本机 PostgreSQL，执行：

   ```sql
   CREATE DATABASE ai_qa_system;
   \c ai_qa_system
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

   若你的 Postgres 未安装 pgvector，请先按 [pgvector 官方说明](https://github.com/pgvector/pgvector#installation) 安装后再执行上述语句。

---

## 四、后端配置与启动

### 4.1 配置环境变量

在项目根目录下，为**后端**创建 `.env` 文件：

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env`，按实际情况修改（至少需改 `DATABASE_URL` 和 `DEEPSEEK_API_KEY`）：

```env
SECRET_KEY=请改为随机字符串
DATABASE_URL=postgresql://postgres:你的postgres密码@localhost:5432/ai_qa_system
DEEPSEEK_API_KEY=你的DeepSeek-API-Key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

- **DATABASE_URL**：数据库连接串，用户名/密码/端口/库名按本机实际情况修改。  
- **DEEPSEEK_API_KEY**：在 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取，用于 AI 问答；不填则无法使用「来自AI知识」的兜底回答，但知识库 RAG 仍可工作（若模型调用不依赖该 Key）。

### 4.2 安装 Python 依赖并执行迁移

在项目根目录下执行（建议在虚拟环境中）：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# 若仅需最小依赖可改用：pip install -r requirements-minimal.txt
python manage.py migrate
```

迁移成功后会创建所需表结构。

### 4.3 启动后端服务

```bash
# 仍在 backend 目录，虚拟环境已激活
python manage.py runserver 0.0.0.0:8000
```

看到类似 `Starting development server at http://0.0.0.0:8000/` 即表示后端已启动。**保持该终端运行。**

---

## 五、前端安装与启动

**新开一个终端**，在项目根目录执行：

```bash
cd frontend
npm install
npm run dev
```

看到类似 `Local: http://localhost:3000/` 即表示前端已启动。前端会把 `/api` 请求代理到本机 8000 端口（后端）。

---

## 六、访问与首次使用

1. **打开浏览器**  
   访问：**http://localhost:3000**

2. **注册 / 登录**  
   首次使用请先注册账号并登录。

3. **创建知识库**  
   在「BIM 知识库与模型」区域创建或选择知识库。

4. **上传 BIM 数据（可选）**  
   支持 `.json` 或 `.ifc` 文件，上传后会自动解析并参与后续问答。

5. **进行问答**  
   在「现场问题 · AI 专业解答」中选择知识库、输入问题并提交。  
   回答会标注「来自知识库」或「来自AI知识」，并支持 Markdown 展示。

---

## 七、一键脚本（可选）

项目根目录下若存在：

- **macOS/Linux**：`./setup.sh` 可引导配置数据库与 `.env`；`./start.sh` 可一次性启动后端与前端（需根据脚本实际内容使用）。
- **Windows**：可双击 `setup.bat` / `start.bat`（若存在）完成配置与启动。

具体以仓库内脚本为准；若不存在，按上述第四、五节手动执行即可。

---

## 八、常见问题

| 现象 | 处理建议 |
|------|----------|
| 克隆失败或提示权限错误 | 使用 SSH 时请确认本机已配置 SSH 公钥并已添加到 GitHub；或改用 HTTPS 克隆。 |
| `relation "knowledge_import_jobs" does not exist` | 未执行迁移或迁移不完整，请在 `backend` 目录执行 `python manage.py migrate`。 |
| 前端访问后端 404 / 跨域 | 确认后端已启动在 8000 端口，且前端使用 `npm run dev`（会代理 `/api` 到 8000）。 |
| AI 回答提示「未配置 AI 模型」 | 在 `backend/.env` 中配置有效的 `DEEPSEEK_API_KEY` 后重启后端。 |
| 推送/拉取时提示 Key is already in use | 表示该 SSH 公钥已在本账号或其它账号使用，无需重复添加，可直接 `git push` / `git pull`。 |

---

## 九、后续更新代码

在项目根目录（smart-ask）下执行：

```bash
git pull origin main
```

若依赖或数据库结构有变更，按项目说明执行（例如后端再次 `pip install -r requirements.txt` 与 `python manage.py migrate`，前端 `npm install`）。

---

*文档版本：v1 | 适用于 smart-ask（BIM 智慧工地问答）从 GitHub 克隆到本地并部署使用。*
