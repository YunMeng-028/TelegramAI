# TelegramAI 智能交互助手

基于密钥授权的Telegram自动化交互工具，通过AI智能生成内容，帮助用户提升Telegram账号的活跃度和曝光量。

## 系统要求

- Python 3.12.x
- Node.js 22.17.1 LTS
- Windows 10/11 (64位)
- 内存 >= 8GB
- 磁盘空间 >= 10GB

## 快速开始

### 1. 环境准备

```bash
# 检查Python版本
python --version  # 应显示 3.12.x

# 检查Node.js版本
node --version    # 应显示 v22.17.1

# 安装Poetry (Python包管理器)
pip install poetry
```

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/TelegramAI.git
cd TelegramAI

# 安装Python依赖
poetry install

# 安装Node.js依赖
npm install
```

### 3. 配置环境

创建 `.env` 文件：

```env
# API配置
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash

# 数据库配置
DATABASE_PATH=data/telegram_ai.db

# ZeroMQ配置
IPC_PORT=5555

# 日志配置
LOG_LEVEL=INFO
```

### 4. 开发模式运行

```bash
# 终端1: 启动Python后端
poetry run python backend/main.py

# 终端2: 启动Electron前端
npm run electron:dev
```

## 项目结构

```
TelegramAI/
├── backend/              # Python后端
│   ├── telegram_ai/      # 核心业务逻辑
│   ├── tests/           # 测试文件
│   └── main.py          # 入口文件
├── frontend/            # Electron前端
│   ├── electron/        # Electron主进程
│   ├── src/            # Vue应用源码
│   └── public/         # 静态资源
├── config/             # 配置文件
├── data/              # 数据目录
├── logs/              # 日志目录
├── docs/              # 文档
├── pyproject.toml     # Python项目配置
├── package.json       # Node.js项目配置
└── README.md         # 本文件
```

## 构建发布

### Windows平台

```bash
# 构建Windows安装包
npm run dist:win
```

构建产物位于 `dist/` 目录。

## 开发指南

### 代码规范

```bash
# Python代码格式化
poetry run black backend/
poetry run ruff check backend/

# 前端代码格式化
npm run lint
npm run format
```

### 运行测试

```bash
# Python测试
poetry run pytest

# 带覆盖率的测试
poetry run pytest --cov=telegram_ai
```

## 许可证

本软件为专有软件，仅供授权用户使用。

## 联系方式

- 技术支持：support@telegramai.com
- 文档中心：docs.telegramai.com

## 免责声明

本软件仅供学习和研究使用。用户需遵守Telegram服务条款和所在地区法律法规。