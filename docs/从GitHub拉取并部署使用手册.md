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

## 二、仓库可见性与同事拉取所需条件

### 2.1 仓库是「公开」还是「私有」？

- **公开仓库（Public）**  
  任何人（包括同事）都可以**无需登录**直接克隆、拉取：  
  `git clone https://github.com/chen8678/smart-ask.git`  
  不需要你额外做任何设置，同事只要本机装了 Git 即可拉取。

- **私有仓库（Private）**  
  只有你本人和被你**添加为协作者（Collaborator）** 的 GitHub 账号可以拉取。同事需要先有自己的 GitHub 账号，再由你把他加入仓库。

### 2.2 如何查看/修改仓库可见性？

1. 打开 **https://github.com/chen8678/smart-ask**
2. 点击 **Settings**（仓库设置）
3. 在 **General** 页最下方 **Danger Zone** 上方，找到 **Visibility**：  
   - 显示 **Public**：当前为公开，任何人可拉取。  
   - 显示 **Private**：当前为私有，需添加协作者后同事才能拉取。

### 2.3 如何让同事能拉取私有仓库？

1. 在仓库页点击 **Settings** → 左侧 **Collaborators**（或 **Collaborators and teams**）
2. 点击 **Add people**，输入同事的 **GitHub 用户名或邮箱**
3. 选择权限（**Read** 即可拉取/克隆），邀请后同事在 GitHub 或邮箱接受邀请即可

同事接受邀请后，用**自己的 GitHub 账号**克隆时使用：

- HTTPS：`git clone https://github.com/chen8678/smart-ask.git`（会提示登录 GitHub）
- SSH：同事本机配置好自己的 SSH 公钥并添加到他的 GitHub 账号后，`git clone git@github.com:chen8678/smart-ask.git`

### 2.4 总结

| 仓库类型 | 同事是否需要 GitHub 账号 | 你是否需要设置 |
|----------|--------------------------|----------------|
| **Public（公开）** | 不需要，可直接克隆 | 不需要 |
| **Private（私有）** | 需要，且需你把他加为协作者 | 在 Settings → Collaborators 中添加 |

---

## 三、从 GitHub 克隆项目

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

## 四、数据库准备

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

## 五、后端配置与启动

### 5.1 配置环境变量

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

### 5.2 安装 Python 依赖并执行迁移

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

### 5.3 启动后端服务

```bash
# 仍在 backend 目录，虚拟环境已激活
python manage.py runserver 0.0.0.0:8000
```

看到类似 `Starting development server at http://0.0.0.0:8000/` 即表示后端已启动。**保持该终端运行。**

---

## 六、前端安装与启动

**新开一个终端**，在项目根目录执行：

```bash
cd frontend
npm install
npm run dev
```

看到类似 `Local: http://localhost:3000/` 即表示前端已启动。前端会把 `/api` 请求代理到本机 8000 端口（后端）。

---

## 七、访问与首次使用

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

## 八、一键脚本（可选）

项目根目录下若存在：

- **macOS/Linux**：`./setup.sh` 可引导配置数据库与 `.env`；`./start.sh` 可一次性启动后端与前端（需根据脚本实际内容使用）。
- **Windows**：可双击 `setup.bat` / `start.bat`（若存在）完成配置与启动。

具体以仓库内脚本为准；若不存在，按上述第五、六节手动执行即可。

---

## 九、常见问题

| 现象 | 处理建议 |
|------|----------|
| 克隆失败或提示权限错误 | 使用 SSH 时请确认本机已配置 SSH 公钥并已添加到 GitHub；或改用 HTTPS 克隆。 |
| `relation "knowledge_import_jobs" does not exist` | 未执行迁移或迁移不完整，请在 `backend` 目录执行 `python manage.py migrate`。 |
| 前端访问后端 404 / 跨域 | 确认后端已启动在 8000 端口，且前端使用 `npm run dev`（会代理 `/api` 到 8000）。 |
| AI 回答提示「未配置 AI 模型」 | 在 `backend/.env` 中配置有效的 `DEEPSEEK_API_KEY` 后重启后端。 |
| 推送/拉取时提示 Key is already in use | 表示该 SSH 公钥已在本账号或其它账号使用，无需重复添加，可直接 `git push` / `git pull`。 |

---

## 十、后续更新代码

在项目根目录（smart-ask）下执行：

```bash
git pull origin main
```

若依赖或数据库结构有变更，按项目说明执行（例如后端再次 `pip install -r requirements.txt` 与 `python manage.py migrate`，前端 `npm install`）。

---

*文档版本：v1 | 适用于 smart-ask（BIM 智慧工地问答）从 GitHub 克隆到本地并部署使用。*
