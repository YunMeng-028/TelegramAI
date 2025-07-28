# TelegramAI 项目开发规则与最佳实践

*最后更新时间：2025-01-28 16:32:00*

## 📋 项目概览

### 1. 技术架构审查

#### ✅ 已完成分析的组件

1. **前端技术栈（Electron + Vue 3）**
   - ✅ Electron 37.2.4 + Vue 3.4.35 桌面应用架构
   - ✅ Element Plus + Tailwind CSS UI框架
   - ✅ TypeScript 5.5.4 + Vite 5.3.5 构建工具
   - ✅ Pinia 状态管理 + Vue Router 路由
   - ✅ ZeroMQ IPC 进程间通信

2. **后端技术栈（Python FastAPI）**
   - ✅ Python 3.12 + Poetry 依赖管理
   - ✅ Telethon 1.40.0 Telegram MTProto 客户端
   - ✅ FastAPI 0.111.1 + Uvicorn 异步 Web 框架
   - ✅ SQLite + aiosqlite 本地数据存储
   - ✅ PyZMQ 27.0.0 进程间通信

3. **Claude Code 集成系统**
   - ✅ TypeScript 和 Python 双端 SDK 实现
   - ✅ 细粒度权限管理系统（PermissionManager）
   - ✅ 工具权限配置（ToolManager）
   - ✅ 三种场景预设：readonly、content_generation、development
   - ✅ 安全的工具白名单机制

### 2. 核心功能识别

**主要功能模块：**
- **AI 智能回复生成**：基于 Claude Code 的上下文感知回复系统
- **多账号管理**：支持多个 Telegram 账号同时运行
- **权限控制**：密钥验证 + RSA-2048 加密授权
- **反检测引擎**：人性化行为模拟和延迟策略
- **监控统计**：实时性能监控和数据分析

## 🔧 开发规则与约定

### 代码风格规范

#### Python 代码规范
```python
# 使用 Black + Ruff + MyPy 工具链
# 配置文件：pyproject.toml

# 代码规范要点：
- 行长度：88 字符
- 类型标注：强制使用 type hints
- 导入顺序：标准库 -> 第三方库 -> 本地模块
- 异步优先：所有 I/O 操作使用 async/await
- 错误处理：使用具体的异常类型，避免裸露的 except
```

#### TypeScript 代码规范
```typescript
// 使用 ESLint + Prettier 工具链
// 配置文件：eslint.config.js

// 代码规范要点：
- 严格的 TypeScript 配置
- 组件命名：PascalCase
- 文件命名：kebab-case
- 接口命名：I 前缀（如 IUser）
- 枚举命名：PascalCase
- 常量命名：UPPER_SNAKE_CASE
```

### 文件组织规范

#### 前端文件结构
```
frontend/
├── src/
│   ├── components/           # 可复用组件
│   ├── views/               # 页面视图
│   ├── stores/              # Pinia 状态管理
│   ├── services/            # 业务服务层
│   │   ├── claude-code/     # Claude Code 服务
│   │   └── ipc/            # IPC 通信
│   ├── types/               # TypeScript 类型定义
│   └── utils/               # 工具函数
└── electron/                # Electron 主进程
```

#### 后端文件结构
```
backend/
└── telegram_ai/
    ├── ai/                  # AI 相关模块
    │   ├── claude_code/     # Claude Code 集成
    │   └── generator.py     # AI 内容生成
    ├── core/                # 核心业务逻辑
    ├── models/              # 数据模型
    ├── services/            # 业务服务
    └── utils/               # 工具函数
```

### Git 工作流规范

#### 分支策略
```bash
# 主分支
main                 # 生产环境代码，仅接受 PR
develop             # 开发主分支

# 功能分支
feature/功能名称     # 新功能开发
fix/bug名称         # Bug修复
hotfix/紧急修复     # 生产环境紧急修复
```

#### 提交规范（使用 Commitizen）
```bash
# 提交类型
feat:      新功能
fix:       Bug修复
docs:      文档更新
style:     代码格式调整
refactor:  代码重构
test:      测试相关
chore:     构建工具/依赖更新

# 示例
npm run commit  # 使用交互式提交
```

### 测试规范

#### Python 测试
```python
# 使用 pytest + pytest-asyncio
# 配置文件：pyproject.toml

# 测试文件命名：test_*.py
# 测试类命名：Test*
# 测试方法命名：test_*

# 运行测试
poetry run pytest                    # 所有测试
poetry run pytest --cov=telegram_ai  # 覆盖率测试
poetry run pytest -m integration     # 集成测试
```

#### TypeScript 测试
```typescript
// 使用 Vitest + Vue Test Utils
// 配置文件：vitest.config.ts

// 测试文件命名：*.test.ts 或 *.spec.ts

// 运行测试
npm run test          // 所有测试
npm run test:ui       // UI 模式
npm run test:coverage // 覆盖率测试
```

## ⚡ 性能优化指南

### 前端性能优化

#### 1. 代码分割与懒加载
```typescript
// 路由懒加载
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/views/Dashboard.vue')
  }
]

// 组件懒加载
const LazyComponent = defineAsyncComponent(() => import('./Component.vue'))
```

#### 2. 状态管理优化
```typescript
// Pinia store 最佳实践
export const useAppStore = defineStore('app', () => {
  // 使用 ref 代替 reactive 减少响应式开销
  const isLoading = ref(false)
  
  // 计算属性缓存
  const expensiveComputed = computed(() => {
    return heavyCalculation()
  })
  
  return { isLoading, expensiveComputed }
}, {
  persist: {
    key: 'app-store',
    storage: localStorage
  }
})
```

### 后端性能优化

#### 1. 数据库优化
```python
# SQLite WAL 模式配置
async def init_database():
    conn = await aiosqlite.connect('telegram_ai.db')
    
    # 性能优化设置
    await conn.execute('PRAGMA journal_mode=WAL')
    await conn.execute('PRAGMA synchronous=NORMAL')
    await conn.execute('PRAGMA cache_size=10000')
    await conn.execute('PRAGMA temp_store=MEMORY')
    
    return conn
```

#### 2. 异步并发优化
```python
# 使用 asyncio.gather 并发执行
async def process_multiple_accounts():
    tasks = [
        process_account(account) 
        for account in accounts
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 使用信号量控制并发数
semaphore = asyncio.Semaphore(5)  # 最多5个并发

async def limited_operation():
    async with semaphore:
        return await expensive_operation()
```

## 🔒 安全开发规范

### 数据保护

#### 1. 敏感信息加密
```python
# Session 数据 AES-256 加密
from cryptography.fernet import Fernet

class SessionManager:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_session(self, session_string: str) -> bytes:
        return self.cipher.encrypt(session_string.encode())
    
    def decrypt_session(self, encrypted_data: bytes) -> str:
        return self.cipher.decrypt(encrypted_data).decode()
```

#### 2. API 密钥管理
```python
# 环境变量管理
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    claude_code_api_key: str
    telegram_api_id: int
    telegram_api_hash: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### Claude Code 权限控制

#### 1. 工具权限最小化原则
```python
# 默认只允许安全工具
safe_tools = {
    ClaudeCodeTool.READ,
    ClaudeCodeTool.GREP,
    ClaudeCodeTool.GLOB,
    ClaudeCodeTool.TODO_WRITE,
    ClaudeCodeTool.WEB_SEARCH
}

# 危险工具需要明确授权
dangerous_tools = {
    ClaudeCodeTool.BASH,
    ClaudeCodeTool.WRITE,
    ClaudeCodeTool.EDIT
}
```

#### 2. 命令过滤规则
```python
# 拒绝危险命令模式
deny_patterns = [
    "Bash(rm -rf*)",      # 删除文件
    "Bash(sudo*)",        # 提权操作
    "Bash(chmod 777*)",   # 危险权限
    "Bash(curl * | sh)",  # 远程执行
]
```

## 🚀 部署与维护

### 开发环境设置

#### 1. 环境准备
```bash
# Python 环境
poetry install
poetry shell

# Node.js 环境
npm install

# 开发服务启动
npm run electron:dev   # 前端开发模式
poetry run python backend/main.py  # 后端服务
```

#### 2. 构建流程
```bash
# 前端构建
npm run build

# Python 打包
poetry build

# 全平台打包
npm run dist:win    # Windows
npm run dist:mac    # macOS
npm run dist:linux  # Linux
```

### 代码质量检查

#### 1. 自动化检查流程
```bash
# Python 代码质量
poetry run black backend/     # 代码格式化
poetry run ruff check backend/  # 语法检查
poetry run mypy backend/      # 类型检查
poetry run bandit -r backend/ # 安全检查

# TypeScript 代码质量
npm run lint        # ESLint 检查
npm run format      # Prettier 格式化
npm run type-check  # TypeScript 检查
```

#### 2. 预提交钩子
```bash
# Husky + lint-staged 配置
npm run prepare  # 安装 git hooks

# 每次提交前自动执行：
# - ESLint 修复
# - Prettier 格式化
# - TypeScript 检查
# - Python 代码检查
```

## 📊 监控与日志

### 应用监控

#### 1. 性能监控
```python
# 性能追踪装饰器
import time
from functools import wraps

def track_performance(operation_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.perf_counter() - start_time
                logger.info(f"{operation_name} 执行时间: {duration:.2f}s")
        return wrapper
    return decorator
```

#### 2. 错误监控
```python
# 结构化日志记录
import structlog

logger = structlog.get_logger()

async def handle_error(error: Exception, context: dict):
    logger.error(
        "操作失败",
        error=str(error),
        error_type=type(error).__name__,
        **context
    )
```

### 日志管理

#### 1. 日志配置
```python
# 使用 loguru 进行日志管理
from loguru import logger

logger.add(
    "logs/telegram_ai_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)
```

#### 2. 日志等级
- **DEBUG**: 详细的开发调试信息
- **INFO**: 一般业务流程信息
- **WARNING**: 警告信息，需要关注
- **ERROR**: 错误信息，需要处理
- **CRITICAL**: 严重错误，系统可能无法继续运行

## 🔄 持续集成与部署

### CI/CD 流程

#### 1. GitHub Actions 工作流
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Python 测试
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        run: poetry run pytest
      
      # Node.js 测试
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '22'
      
      - name: Install dependencies
        run: npm install
      
      - name: Run tests
        run: npm run test
```

#### 2. 构建与发布
```bash
# 版本发布流程
npm run commit              # 提交代码
git push origin develop     # 推送到开发分支
gh pr create               # 创建 Pull Request
# 代码审查通过后合并到 main
npm run dist               # 构建发布版本
```

## 📚 文档维护

### 开发文档

#### 1. API 文档
- 后端 API：使用 FastAPI 自动生成 OpenAPI 文档
- 前端组件：使用 Storybook 进行组件文档化

#### 2. 架构文档
- 系统架构图
- 数据流图
- 权限管理流程图
- Claude Code 集成架构

### 用户文档

#### 1. 用户手册
- 安装配置指南
- 功能使用说明
- 故障排除指南
- FAQ 常见问题

#### 2. 开发者文档
- 项目设置指南
- 开发环境配置
- 贡献代码指南
- 发布流程说明

---

## 🎯 下一步行动项

### 即将完成的任务

- [ ] **代码规范审查**
  - [ ] 检查现有代码是否符合制定的规范
  - [ ] 添加缺失的类型标注和文档注释
  - [ ] 配置和测试所有代码质量工具

- [ ] **测试覆盖率提升**
  - [ ] 编写核心模块的单元测试
  - [ ] 添加 Claude Code 集成测试
  - [ ] 配置 CI/CD 自动化测试

- [ ] **性能优化实施**
  - [ ] 数据库查询优化
  - [ ] 前端组件懒加载
  - [ ] 缓存策略实现

- [ ] **安全加固**
  - [ ] 权限系统完善
  - [ ] 数据加密实现
  - [ ] 安全审计工具集成

### 长期规划

1. **功能增强**（第2季度）
   - Claude Code 工具权限细化
   - 多语言支持
   - 插件系统架构

2. **性能优化**（第3季度）
   - 大规模并发优化
   - 内存使用优化
   - 响应时间优化

3. **生态建设**（第4季度）
   - 开发者社区建设
   - 插件市场
   - 云服务版本

---

*本文档将根据项目发展持续更新，确保开发规范与项目实际需求保持同步。*