#!/bin/bash

# TelegramAI 开发环境设置脚本
set -e

echo "🚀 TelegramAI 开发环境设置开始..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查必要工具
check_requirements() {
    echo -e "${BLUE}📋 检查系统要求...${NC}"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装，请先安装 Node.js 22.x${NC}"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | sed 's/v//')
    REQUIRED_NODE="22.0.0"
    if [ "$(printf '%s\n' "$REQUIRED_NODE" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE" ]; then
        echo -e "${RED}❌ Node.js 版本过低，需要 22.x，当前版本: $NODE_VERSION${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装，请先安装 Python 3.12${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    REQUIRED_PYTHON="3.12.0"
    if [ "$(printf '%s\n' "$REQUIRED_PYTHON" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_PYTHON" ]; then
        echo -e "${YELLOW}⚠️  推荐使用 Python 3.12，当前版本: $PYTHON_VERSION${NC}"
    else
        echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
    fi
    
    # 检查Poetry
    if ! command -v poetry &> /dev/null; then
        echo -e "${YELLOW}📦 Poetry 未安装，正在安装...${NC}"
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    fi
    echo -e "${GREEN}✅ Poetry$(poetry --version | awk '{print $3}')${NC}"
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git 未安装${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Git$(git --version | awk '{print $3}')${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}📦 安装项目依赖...${NC}"
    
    # 安装Python依赖
    echo -e "${YELLOW}正在安装Python依赖...${NC}"
    poetry install
    
    # 安装Node.js依赖
    echo -e "${YELLOW}正在安装Node.js依赖...${NC}"
    npm install
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 设置环境变量
setup_environment() {
    echo -e "${BLUE}⚙️  设置环境变量...${NC}"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${GREEN}✅ 创建 .env 文件${NC}"
            echo -e "${YELLOW}⚠️  请编辑 .env 文件并填入必要的配置${NC}"
        else
            echo -e "${YELLOW}⚠️  .env.example 文件不存在${NC}"
        fi
    else
        echo -e "${GREEN}✅ .env 文件已存在${NC}"
    fi
}

# 设置Git钩子
setup_git_hooks() {
    echo -e "${BLUE}🔧 设置Git钩子...${NC}"
    
    # 安装pre-commit
    if ! command -v pre-commit &> /dev/null; then
        echo -e "${YELLOW}正在安装pre-commit...${NC}"
        poetry run pip install pre-commit
    fi
    
    # 安装Git钩子
    poetry run pre-commit install
    poetry run pre-commit install --hook-type commit-msg
    
    # 安装Husky钩子
    npm run prepare
    
    echo -e "${GREEN}✅ Git钩子设置完成${NC}"
}

# 初始化数据库
init_database() {
    echo -e "${BLUE}🗄️  初始化数据库...${NC}"
    
    # 创建数据目录
    mkdir -p data/sessions data/backups data/cache
    mkdir -p logs
    
    # 运行数据库迁移（如果存在）
    if [ -f "backend/telegram_ai/database.py" ]; then
        poetry run python backend/telegram_ai/database.py
        echo -e "${GREEN}✅ 数据库初始化完成${NC}"
    else
        echo -e "${YELLOW}⚠️  数据库迁移脚本不存在，跳过${NC}"
    fi
}

# 运行代码质量检查
run_quality_checks() {
    echo -e "${BLUE}🔍 运行代码质量检查...${NC}"
    
    # Python代码检查
    echo -e "${YELLOW}检查Python代码...${NC}"
    poetry run black --check backend/ || echo -e "${YELLOW}⚠️  Python代码格式需要修复${NC}"
    poetry run ruff check backend/ || echo -e "${YELLOW}⚠️  Python代码质量需要改进${NC}"
    
    # 前端代码检查
    echo -e "${YELLOW}检查前端代码...${NC}"
    npm run lint || echo -e "${YELLOW}⚠️  前端代码质量需要改进${NC}"
    npm run type-check || echo -e "${YELLOW}⚠️  TypeScript类型检查失败${NC}"
    
    echo -e "${GREEN}✅ 代码质量检查完成${NC}"
}

# 运行测试
run_tests() {
    echo -e "${BLUE}🧪 运行测试...${NC}"
    
    # Python测试
    echo -e "${YELLOW}运行Python测试...${NC}"
    if poetry run pytest backend/tests/ --tb=short; then
        echo -e "${GREEN}✅ Python测试通过${NC}"
    else
        echo -e "${YELLOW}⚠️  部分Python测试失败${NC}"
    fi
    
    # 前端测试
    echo -e "${YELLOW}运行前端测试...${NC}"
    if npm run test; then
        echo -e "${GREEN}✅ 前端测试通过${NC}"
    else
        echo -e "${YELLOW}⚠️  部分前端测试失败${NC}"
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${BLUE}📚 开发环境使用说明:${NC}"
    echo ""
    echo -e "${GREEN}启动开发服务器:${NC}"
    echo "  npm run electron:dev    # 启动Electron应用"
    echo "  poetry run python backend/main.py  # 启动Python后端"
    echo ""
    echo -e "${GREEN}代码质量检查:${NC}"
    echo "  npm run lint           # 前端代码检查"
    echo "  poetry run black backend/  # Python代码格式化"
    echo "  poetry run ruff check backend/  # Python代码检查"
    echo ""
    echo -e "${GREEN}运行测试:${NC}"
    echo "  npm run test           # 前端测试"
    echo "  poetry run pytest     # Python测试"
    echo ""
    echo -e "${GREEN}构建应用:${NC}"
    echo "  npm run build         # 构建前端"
    echo "  npm run dist:win      # 构建Windows安装包"
    echo ""
    echo -e "${GREEN}Docker开发环境:${NC}"
    echo "  docker-compose -f docker-compose.dev.yml up  # 启动开发容器"
    echo ""
    echo -e "${YELLOW}🔧 配置文件位置:${NC}"
    echo "  .env                   # 环境变量配置"
    echo "  .vscode/settings.json  # VS Code配置"
    echo "  eslint.config.js       # ESLint配置"
    echo "  pyproject.toml         # Python项目配置"
}

# 主函数
main() {
    echo -e "${GREEN}"
    echo "██████╗ ███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗ █████╗ ██╗"
    echo "╚══██╔╝ ██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║██╔══██╗██║"
    echo "  ██╔╝  █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║███████║██║"
    echo " ██╔╝   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║██╔══██║██║"
    echo "██╔╝    ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║██║"
    echo "╚═╝     ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝"
    echo -e "${NC}"
    echo -e "${BLUE}TelegramAI 智能交互助手 - 开发环境设置${NC}"
    echo ""
    
    check_requirements
    install_dependencies
    setup_environment
    setup_git_hooks
    init_database
    
    # 可选步骤
    read -p "是否运行代码质量检查？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_quality_checks
    fi
    
    read -p "是否运行测试？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    echo ""
    echo -e "${GREEN}🎉 开发环境设置完成！${NC}"
    show_usage
}

# 脚本参数处理
case "${1:-}" in
    "check")
        check_requirements
        ;;
    "install")
        install_dependencies
        ;;
    "hooks")
        setup_git_hooks
        ;;
    "test")
        run_tests
        ;;
    "quality")
        run_quality_checks
        ;;
    *)
        main
        ;;
esac