#!/bin/bash

# TelegramAI 构建脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VERSION=${1:-$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")}
BUILD_DIR="dist"
PLATFORM=${2:-$(uname -s | tr '[:upper:]' '[:lower:]')}

echo -e "${BLUE}🏗️  TelegramAI 构建脚本${NC}"
echo -e "${BLUE}版本: ${GREEN}$VERSION${NC}"
echo -e "${BLUE}平台: ${GREEN}$PLATFORM${NC}"
echo ""

# 清理构建目录
clean_build() {
    echo -e "${YELLOW}🧹 清理构建目录...${NC}"
    rm -rf $BUILD_DIR
    rm -rf dist-electron
    rm -rf backend/dist
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "${YELLOW}📦 检查并安装依赖...${NC}"
    
    # 检查Node.js依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装Node.js依赖...${NC}"
        npm ci
    fi
    
    # 检查Python依赖
    if ! poetry show &>/dev/null; then
        echo -e "${YELLOW}安装Python依赖...${NC}"
        poetry install --no-dev
    fi
    
    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 代码质量检查
quality_check() {
    echo -e "${YELLOW}🔍 运行代码质量检查...${NC}"
    
    # Python代码检查
    echo -e "${BLUE}检查Python代码...${NC}"
    poetry run black --check backend/ || {
        echo -e "${RED}❌ Python代码格式检查失败${NC}"
        exit 1
    }
    
    poetry run ruff check backend/ || {
        echo -e "${RED}❌ Python代码质量检查失败${NC}"
        exit 1
    }
    
    poetry run mypy backend/ || {
        echo -e "${YELLOW}⚠️  Python类型检查有警告${NC}"
    }
    
    # 前端代码检查
    echo -e "${BLUE}检查前端代码...${NC}"
    npm run lint || {
        echo -e "${RED}❌ 前端代码质量检查失败${NC}"
        exit 1
    }
    
    npm run type-check || {
        echo -e "${RED}❌ TypeScript类型检查失败${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✅ 代码质量检查通过${NC}"
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}🧪 运行测试套件...${NC}"
    
    # Python测试
    echo -e "${BLUE}运行Python测试...${NC}"
    poetry run pytest backend/tests/ --cov=telegram_ai --cov-report=xml || {
        echo -e "${RED}❌ Python测试失败${NC}"
        exit 1
    }
    
    # 前端测试
    echo -e "${BLUE}运行前端测试...${NC}"
    npm run test:coverage || {
        echo -e "${RED}❌ 前端测试失败${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✅ 所有测试通过${NC}"
}

# 构建前端
build_frontend() {
    echo -e "${YELLOW}🎨 构建前端应用...${NC}"
    
    # 设置构建环境变量
    export NODE_ENV=production
    export VITE_VERSION=$VERSION
    export VITE_BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # 构建Vue应用
    npm run build
    
    echo -e "${GREEN}✅ 前端构建完成${NC}"
}

# 构建后端
build_backend() {
    echo -e "${YELLOW}🐍 构建Python后端...${NC}"
    
    # 创建后端构建目录
    mkdir -p backend/dist
    
    # 复制Python代码
    cp -r backend/telegram_ai backend/dist/
    cp backend/main.py backend/dist/
    
    # 生成requirements.txt
    poetry export -f requirements.txt --output backend/dist/requirements.txt --without-hashes
    
    # 清理Python缓存
    find backend/dist -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find backend/dist -name "*.pyc" -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ 后端构建完成${NC}"
}

# 打包Electron应用
package_electron() {
    echo -e "${YELLOW}📦 打包Electron应用...${NC}"
    
    case $PLATFORM in
        "windows"|"win32")
            npm run dist:win
            ;;
        "darwin"|"macos")
            npm run dist:mac
            ;;
        "linux")
            npm run dist:linux
            ;;
        *)
            echo -e "${YELLOW}⚠️  未知平台: $PLATFORM，尝试通用构建...${NC}"
            npm run electron:build
            ;;
    esac
    
    echo -e "${GREEN}✅ Electron应用打包完成${NC}"
}

# 生成构建信息
generate_build_info() {
    echo -e "${YELLOW}📋 生成构建信息...${NC}"
    
    BUILD_INFO_FILE="$BUILD_DIR/build-info.json"
    
    cat > $BUILD_INFO_FILE << EOF
{
  "version": "$VERSION",
  "buildTime": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "platform": "$PLATFORM",
  "gitCommit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "gitBranch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')",
  "nodeVersion": "$(node --version)",
  "npmVersion": "$(npm --version)",
  "pythonVersion": "$(python3 --version | cut -d' ' -f2)",
  "poetryVersion": "$(poetry --version | cut -d' ' -f3)"
}
EOF
    
    echo -e "${GREEN}✅ 构建信息生成完成${NC}"
}

# 创建发布包
create_release_package() {
    echo -e "${YELLOW}📦 创建发布包...${NC}"
    
    RELEASE_NAME="TelegramAI-$VERSION-$PLATFORM"
    RELEASE_DIR="releases/$RELEASE_NAME"
    
    # 创建发布目录
    mkdir -p $RELEASE_DIR
    
    # 复制构建产物
    if [ -d "$BUILD_DIR" ]; then
        cp -r $BUILD_DIR/* $RELEASE_DIR/
    fi
    
    # 复制必要文件
    cp README.md $RELEASE_DIR/
    cp LICENSE $RELEASE_DIR/ 2>/dev/null || echo "LICENSE文件不存在"
    cp .env.example $RELEASE_DIR/
    
    # 创建安装脚本
    cat > $RELEASE_DIR/install.sh << 'EOF'
#!/bin/bash
echo "TelegramAI 安装脚本"
echo "请确保已安装Node.js 22.x和Python 3.12"
echo ""
echo "1. 复制.env.example为.env并配置"
echo "2. 运行应用程序"
EOF
    
    chmod +x $RELEASE_DIR/install.sh
    
    # 创建压缩包
    cd releases
    tar -czf "$RELEASE_NAME.tar.gz" "$RELEASE_NAME"
    cd ..
    
    echo -e "${GREEN}✅ 发布包创建完成: releases/$RELEASE_NAME.tar.gz${NC}"
}

# 显示构建摘要
show_summary() {
    echo ""
    echo -e "${GREEN}🎉 构建完成！${NC}"
    echo -e "${BLUE}构建摘要:${NC}"
    echo -e "  版本: ${GREEN}$VERSION${NC}"
    echo -e "  平台: ${GREEN}$PLATFORM${NC}"
    echo -e "  构建时间: ${GREEN}$(date)${NC}"
    echo ""
    
    if [ -d "$BUILD_DIR" ]; then
        echo -e "${BLUE}构建产物:${NC}"
        ls -la $BUILD_DIR/
        echo ""
        
        # 显示文件大小
        echo -e "${BLUE}文件大小:${NC}"
        du -hs $BUILD_DIR/*
    fi
    
    if [ -d "releases" ]; then
        echo ""
        echo -e "${BLUE}发布包:${NC}"
        ls -la releases/*.tar.gz 2>/dev/null || echo "无发布包"
    fi
}

# 主函数
main() {
    echo -e "${GREEN}"
    echo "████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗ █████╗ ██╗"
    echo "╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║██╔══██╗██║"
    echo "   ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║███████║██║"
    echo "   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║██╔══██║██║"
    echo "   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║██║"
    echo "   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝"
    echo -e "${NC}"
    echo -e "${BLUE}TelegramAI 构建系统${NC}"
    echo ""
    
    clean_build
    install_dependencies
    quality_check
    run_tests
    build_frontend
    build_backend
    package_electron
    generate_build_info
    create_release_package
    show_summary
}

# 脚本参数处理
case "${1:-}" in
    "--help"|"-h")
        echo "用法: $0 [版本] [平台]"
        echo ""
        echo "参数:"
        echo "  版本    构建版本号 (默认: git tag)"
        echo "  平台    目标平台 (windows|macos|linux, 默认: 当前平台)"
        echo ""
        echo "示例:"
        echo "  $0                    # 使用默认版本和平台"
        echo "  $0 v1.2.0            # 指定版本"
        echo "  $0 v1.2.0 windows    # 指定版本和平台"
        exit 0
        ;;
    "--clean")
        clean_build
        exit 0
        ;;
    "--check")
        quality_check
        run_tests
        exit 0
        ;;
    *)
        main
        ;;
esac