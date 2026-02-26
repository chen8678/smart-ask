# 打包给 Windows 同事测试说明

## 方式一：复制出一份「测试用最小包」（推荐）

只包含当前流程用到的代码，体积更小、结构更清晰。

**步骤**：在 **chen-AI** 目录下执行：

```bash
cd /path/to/chen-AI
python copy_test_package.py
```

会在 **chen-AI 上一级目录** 生成 **`chen-AI-测试包`**，内含：

- **backend/**：仅 auth、knowledge、chat、system、simple_api 五个 app，以及最小化 `settings.py`、`urls.py`（无 learning/legal/medical 等）
- **frontend/**：完整前端（已排除 node_modules、dist）
- **docs/**：BIM 部署说明、本说明、问答与 AI-Key 说明
- **README-测试包.md**：Windows 快速启动说明

然后将 **`chen-AI-测试包`** 整目录压缩为 zip 发给同事即可。同事解压后按包内 `README-测试包.md` 和 `docs/打包给Windows同事测试说明.md` 操作。

---

## 方式二：直接压缩 chen-AI（排除大目录）

**结论**：**直接压缩整个 chen-AI 文件夹**也可，排除大目录后发给同事。  
当前跑通的流程（登录 → 知识库 → BIM 上传 → AI 问答）都在 chen-AI 里，同事在 Windows 上按下面步骤即可复现。

为减小压缩包体积、避免把本机环境打进包，压缩前请**排除**以下目录/文件（不要打进 zip）：

| 排除项 | 说明 |
|--------|------|
| `backend/__pycache__/`、所有 `**/__pycache__/` | Python 缓存 |
| `backend/venv/`、`backend/.venv/`、`backend/env/` | Python 虚拟环境（同事本机自建） |
| `frontend/node_modules/` | 前端依赖（同事本机 `npm install`） |
| `frontend/dist/` | 前端构建产物（可选排除） |
| `.git/` | 若不需要版本历史可排除 |
| `backend/media/`、`backend/staticfiles/`、`backend/*.log`、`*.sqlite3` | 本地运行时生成 |

**压缩方式示例**（任选其一）：

- **一键打包（推荐）**：在 **MAXkb** 目录（chen-AI 的上一级）执行：  
  `bash chen-AI/package_for_windows.sh`  
  会在当前目录生成 `chen-AI-Windows测试包-YYYYMMDD.zip`，已自动排除上述大目录。
- **macOS / Linux 手动**：在 chen-AI 上一级目录执行：  
  `zip -r chen-AI-测试包.zip chen-AI -x "chen-AI/frontend/node_modules/*" -x "chen-AI/*/__pycache__/*" -x "chen-AI/backend/venv/*" -x "chen-AI/backend/.venv/*" -x "chen-AI/.git/*" -x "chen-AI/frontend/dist/*"`
- **手动**：复制整个 chen-AI 到新文件夹，删掉上表中的目录后再压缩该文件夹。

压缩包内建议保留：

- `backend/`（含 `requirements.txt`、`ai_qa_system/`、`apps/` 等）
- `frontend/`（含 `package.json`、`src/` 等）
- `docs/`（含本说明、BIM 部署说明、问答与 AI-Key 说明）
- `backend/.env.example`（若有）或说明里写明需配置的环境变量

---

## 二、不推荐：单独“分离出用到的代码”

当前用到的模块包括：

- 后端：`apps.auth`、`apps.knowledge`（含 BIM）、`apps.chat`、`apps.simple_api`、`apps.system`（API 配置）、Django 配置与路由、向量化/检索等。
- 前端：登录、首页（知识库 + BIM 上传 + 问答）、路由、请求封装、Pinia 等。

这些和“未用到的”模块（学习、法律、医疗、金融等）在同一个 Django 项目里，路由和配置是共用的。若只拷贝“用到的 app”，需要改 `INSTALLED_APPS`、`urls.py`、可能还有静态/模板路径，容易漏配、增加维护成本。  
因此**建议始终打包整个 chen-AI**，用“排除大目录”的方式控体积即可。

---

## 三、Windows 同事本地测试步骤

### 1. 环境准备

- **Python 3.9+**（建议 3.9 或 3.10）
- **Node.js 18+**
- **PostgreSQL 12+**（需支持 pgvector 扩展；若没有可先用 SQLite 做最小测试，见下）
- 可选：**ifcopenshell**（仅在上传 .ifc 时需要）

### 2. 解压与后端

```text
解压 chen-AI-测试包.zip 到任意目录，例如 D:\chen-AI

打开 cmd 或 PowerShell：

cd D:\chen-AI\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install ifcopenshell
```

若本机**没有 PostgreSQL**，可先用 SQLite 做接口测试（需改配置，见项目 `docs/BIM知识库与AI问答-部署说明.md` 或 `backend/ai_qa_system/settings.py` 中 `DATABASES`）。正式测试建议仍用 PostgreSQL + pgvector。

### 3. 环境变量 / .env

在 `backend` 目录下新建或编辑 `.env`，至少保证：

- `SECRET_KEY`：Django 密钥
- `DATABASE_URL` 或 `DATABASES`：数据库连接（若用 SQLite 可省略）
- `DEEPSEEK_API_KEY`（或你当前用的 AI Key）：用于 AI 问答

可参考 `docs/问答链路与AI-Key配置说明.md`。

### 4. 数据库迁移与启动后端

```text
cd D:\chen-AI\backend
.venv\Scripts\activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 5. 前端

新开一个终端：

```text
cd D:\chen-AI\frontend
npm install
npm run dev
```

### 6. 访问

浏览器打开：**http://localhost:3000**  
先注册/登录，再创建知识库、上传 BIM（.json 或 .ifc）、进行 AI 问答。

---

## 四、若压缩包仍然很大

可再排除：

- `vectorization-service/`（若同事不跑向量化微服务，用后端内置 TF-IDF 降级即可）
- 根目录下与本次测试无关的 `.md`、`.sh`、测试脚本等

核心保留：`backend/`、`frontend/`、`docs/` 及本说明。

---

**总结**：直接压缩 **chen-AI**，压缩前排除 `node_modules`、`__pycache__`、`venv`/`.venv`、`.git`、`dist` 等；把本说明和 `docs/BIM知识库与AI问答-部署说明.md`、`docs/问答链路与AI-Key配置说明.md` 一并发给同事即可在 Windows 上复现测试。
