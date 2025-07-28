# TelegramAI 开发指南

## 开发环境设置

### 前置要求

- Python 3.12.x
- Node.js 22.17.1 LTS
- Git
- Visual Studio Code (推荐)

### 推荐的 VS Code 扩展

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "Vue.volar",
    "Vue.vscode-typescript-vue-plugin",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "antfu.iconify",
    "mikestead.dotenv",
    "EditorConfig.EditorConfig"
  ]
}
```

### 环境初始化

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd TelegramAI
   ```

2. **配置 Python 环境**
   ```bash
   # 安装 Poetry
   pip install poetry

   # 安装依赖
   poetry install

   # 激活虚拟环境
   poetry shell
   ```

3. **配置 Node.js 环境**
   ```bash
   # 安装依赖
   npm install

   # 安装 Husky Git 钩子
   npm run prepare
   ```

4. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.example .env

   # 编辑 .env 文件，填入必要的配置
   ```

## 开发工具链

### Python 工具

| 工具 | 用途 | 命令 |
|------|------|------|
| Black | 代码格式化 | `poetry run black backend/` |
| Ruff | 代码检查 | `poetry run ruff check backend/` |
| MyPy | 类型检查 | `poetry run mypy backend/` |
| Pytest | 单元测试 | `poetry run pytest` |
| Coverage | 测试覆盖率 | `poetry run pytest --cov` |
| Bandit | 安全检查 | `poetry run bandit -r backend/` |

### 前端工具

| 工具 | 用途 | 命令 |
|------|------|------|
| ESLint | 代码检查 | `npm run lint` |
| Prettier | 代码格式化 | `npm run format` |
| TypeScript | 类型检查 | `npm run type-check` |
| Vitest | 单元测试 | `npm run test` |
| Vite | 开发服务器 | `npm run dev` |

### Git 工作流

1. **提交前检查**
   - pre-commit 钩子会自动运行代码格式化和检查
   - commit-msg 钩子会验证提交信息格式

2. **提交信息规范**
   ```
   <type>(<scope>): <subject>
   
   <body>
   
   <footer>
   ```
   
   类型包括：feat, fix, docs, style, refactor, perf, test, build, ci, chore

3. **使用 Commitizen**
   ```bash
   npm run commit
   ```

## 项目结构

```
TelegramAI/
├── backend/                 # Python 后端
│   ├── telegram_ai/        # 核心模块
│   │   ├── api/           # FastAPI 路由
│   │   ├── core/          # 核心功能
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   └── utils/         # 工具函数
│   └── tests/             # 测试文件
├── frontend/               # Electron + Vue 前端
│   ├── electron/          # Electron 主进程
│   ├── src/              # Vue 应用源码
│   │   ├── api/          # API 调用
│   │   ├── components/   # 组件
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── views/        # 页面视图
│   │   └── utils/        # 工具函数
│   └── types/            # TypeScript 类型定义
├── config/                # 配置文件
├── docs/                  # 文档
├── resources/             # 资源文件
└── scripts/               # 脚本文件
```

## 开发流程

### 启动开发环境

1. **启动 Python 后端**
   ```bash
   poetry run python backend/main.py
   ```

2. **启动 Electron 前端**
   ```bash
   npm run electron:dev
   ```

### 运行测试

```bash
# Python 测试
poetry run pytest
poetry run pytest --cov  # 带覆盖率

# 前端测试
npm run test
npm run test:ui       # UI 模式
npm run test:coverage # 覆盖率报告
```

### 代码质量检查

```bash
# Python
poetry run black backend/ --check
poetry run ruff check backend/
poetry run mypy backend/
poetry run bandit -r backend/

# 前端
npm run lint
npm run type-check
```

## 调试技巧

### Python 调试

1. **使用 ipdb**
   ```python
   import ipdb; ipdb.set_trace()
   ```

2. **VS Code 调试配置**
   ```json
   {
     "name": "Python: FastAPI",
     "type": "python",
     "request": "launch",
     "module": "uvicorn",
     "args": ["telegram_ai.main:app", "--reload"],
     "jinja": true
   }
   ```

### Electron 调试

1. **开发者工具**
   - 在开发模式下自动打开
   - 使用 `Ctrl+Shift+I` 手动打开

2. **VS Code 调试配置**
   ```json
   {
     "name": "Electron: Main",
     "type": "node",
     "request": "launch",
     "protocol": "inspector",
     "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron",
     "windows": {
       "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron.cmd"
     },
     "args": ["."],
     "env": {
       "NODE_ENV": "development"
     }
   }
   ```

## 性能优化

### Python 性能分析

```python
# 使用 cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# 你的代码
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats()
```

### 前端性能优化

1. **代码分割**
   - 路由懒加载
   - 动态导入组件

2. **打包优化**
   - 见 `vite.config.ts` 中的 `manualChunks` 配置

## 故障排查

### 常见问题

1. **Poetry 安装失败**
   ```bash
   # 清理缓存
   poetry cache clear pypi --all
   # 更新 Poetry
   pip install --upgrade poetry
   ```

2. **Electron 构建失败**
   ```bash
   # 重新安装 electron
   npm run postinstall
   # 清理缓存
   npm cache clean --force
   ```

3. **ZeroMQ 编译错误**
   - Windows: 需要 Visual Studio Build Tools
   - Linux: 需要 `sudo apt-get install libzmq3-dev`
   - macOS: 需要 `brew install zeromq`

## 发布流程

1. **版本更新**
   ```bash
   # 自动更新版本号
   poetry run bump-my-version patch  # 或 minor, major
   ```

2. **构建发布包**
   ```bash
   # Windows
   npm run dist:win
   
   # macOS
   npm run dist:mac
   
   # Linux
   npm run dist:linux
   ```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`npm run commit`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 相关资源

- [Telethon 文档](https://docs.telethon.dev/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Electron 文档](https://www.electronjs.org/)
- [项目 Wiki](https://github.com/yourproject/wiki)