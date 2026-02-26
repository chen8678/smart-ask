# 给同事的使用说明

> **避免乱码**：`setup.bat` 和 `start.bat` 已改为英文提示，在 Windows 下不会乱码。  
> 英文含义对照见 `运行说明-避免乱码.txt`，中文详细步骤见下方。

## 🎯 快速开始（3步搞定）

### 1️⃣ 解压测试包
将 `chen-AI-测试包.zip` 解压到任意目录

### 2️⃣ 双击运行 `setup.bat`
按照提示输入：
- PostgreSQL密码（安装PostgreSQL时设置的）
- 数据库名称（直接回车用默认值）
- API Key（可选，稍后可添加）

### 3️⃣ 双击运行 `start.bat`
等待服务启动，然后访问 http://localhost:3000

---

## 📋 详细步骤

### 第一步：环境准备

确保已安装：
- ✅ **Python 3.9+** - https://www.python.org/downloads/
- ✅ **Node.js 18+** - https://nodejs.org/
- ✅ **PostgreSQL 14+** - https://www.postgresql.org/download/windows/

> 💡 **提示**：安装Python时记得勾选"Add Python to PATH"

### 第二步：一键配置

1. **进入解压后的目录**
   ```
   例如：D:\chen-AI-测试包
   ```

2. **双击 `setup.bat`**
   - 如果提示"需要安装Python3"或"需要安装Node.js"，请先安装对应软件
   - 按照提示输入配置信息

3. **创建数据库**（如果提示）
   - 打开命令提示符
   - 执行：`psql -U postgres`
   - 输入postgres密码
   - 执行：
     ```sql
     CREATE DATABASE ai_qa_system;
     \c ai_qa_system
     CREATE EXTENSION IF NOT EXISTS vector;
     \q
     ```

### 第三步：一键启动

1. **双击 `start.bat`**
   - 会自动打开两个窗口（后端和前端）
   - 等待启动完成

2. **访问系统**
   - 浏览器打开：http://localhost:3000
   - 注册账号
   - 开始使用

---

## ❓ 常见问题

### Q1: 提示"需要安装Python3"
**A:** 访问 https://www.python.org/downloads/ 下载安装，安装时勾选"Add Python to PATH"

### Q2: 提示"需要安装Node.js"
**A:** 访问 https://nodejs.org/ 下载LTS版本安装

### Q3: PostgreSQL密码忘记了
**A:** 
- 方法1：按 `Win+R` → 输入 `services.msc` → 找到PostgreSQL服务 → 查看属性
- 方法2：重新安装PostgreSQL并记住密码

### Q4: PostgreSQL服务未运行
**A:** 
- 按 `Win+R` → 输入 `services.msc`
- 找到 `postgresql-x64-14` 或类似服务
- 右键 → 启动

### Q5: 端口被占用（8000或3000）
**A:** 关闭占用端口的程序，或重启电脑

### Q6: 数据库连接失败
**A:** 
- 检查PostgreSQL服务是否运行
- 检查 `backend/.env` 中的密码是否正确
- 确认数据库已创建

---

## 📚 更多帮助

- **完整指南**：查看 `使用指南-一键配置.md`
- **快速参考**：查看 `README-测试包.md`
- **BIM功能**：查看 `docs/BIM知识库与AI问答-部署说明.md`

---

## 🎉 开始使用

配置完成后，访问 http://localhost:3000 开始使用！

**功能包括：**
- ✅ 用户注册/登录
- ✅ 知识库管理
- ✅ BIM文件上传（.json/.ifc）
- ✅ AI智能问答
