# 智能知识问答 · 测试包（登录 + 知识库 + BIM + AI 问答）

本目录为从 chen-AI 复制出的「当前流程最小集」，便于在 Windows 上快速测试。

> 📖 **详细使用指南**：请查看 `使用指南-一键配置.md`（包含完整步骤和常见问题解答）

## ⚙️ 首次使用：一键配置

### macOS/Linux

```bash
./setup.sh
```

### Windows

双击运行 `setup.bat` 或在命令行执行：

```cmd
setup.bat
```

配置脚本会引导你：
- ✅ 输入数据库配置信息
- ✅ 生成 `backend/.env` 配置文件
- ✅ 创建数据库和安装 pgvector 扩展
- ✅ 安装 Python 依赖并执行数据库迁移

## 🚀 一键启动

配置完成后，使用启动脚本：

### macOS/Linux

```bash
./start.sh
```

### Windows

双击运行 `start.bat` 或在命令行执行：

```cmd
start.bat
```

启动脚本会自动：
- ✅ 检查并启动 PostgreSQL
- ✅ 验证数据库连接
- ✅ 启动后端和前端服务

## 📋 手动启动（备选方案）

### 1. 环境要求

- Python 3.9+
- Node.js 18+
- PostgreSQL（需 pgvector 扩展）

### 2. 配置环境变量

在 `backend` 目录新建 `.env` 文件：

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:你的密码@localhost:5432/ai_qa_system
DEEPSEEK_API_KEY=你的Key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### 3. 后端启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-minimal.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 4. 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 5. 访问

浏览器打开：http://localhost:3000  
先注册/登录，再创建知识库、上传 BIM（.json/.ifc）、进行 AI 问答。

## 📚 详细说明

- `docs/打包给Windows同事测试说明.md` - 完整部署指南
- `docs/BIM知识库与AI问答-部署说明.md` - BIM功能说明
