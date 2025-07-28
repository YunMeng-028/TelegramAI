#!/bin/bash

# TelegramAI 部署脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
DEPLOY_USER=${DEPLOY_USER:-"telegramai"}
DEPLOY_HOST=${DEPLOY_HOST:-"localhost"}
DEPLOY_PATH=${DEPLOY_PATH:-"/opt/telegramai"}
SERVICE_NAME=${SERVICE_NAME:-"telegramai"}
BACKUP_DIR=${BACKUP_DIR:-"/opt/telegramai/backups"}
VERSION=${1:-$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")}

echo -e "${BLUE}🚀 TelegramAI 部署脚本${NC}"
echo -e "${BLUE}版本: ${GREEN}$VERSION${NC}"
echo -e "${BLUE}目标: ${GREEN}$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH${NC}"
echo ""

# 检查SSH连接
check_ssh_connection() {
    echo -e "${YELLOW}🔗 检查SSH连接...${NC}"
    
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $DEPLOY_USER@$DEPLOY_HOST exit 2>/dev/null; then
        echo -e "${RED}❌ 无法连接到目标服务器${NC}"
        echo -e "${YELLOW}请确保:${NC}"
        echo "  1. SSH密钥已配置"
        echo "  2. 目标服务器可访问"
        echo "  3. 用户权限正确"
        exit 1
    fi
    
    echo -e "${GREEN}✅ SSH连接正常${NC}"
}

# 检查构建产物
check_build_artifacts() {
    echo -e "${YELLOW}📦 检查构建产物...${NC}"
    
    if [ ! -d "dist" ]; then
        echo -e "${RED}❌ 构建产物不存在，请先运行构建${NC}"
        echo "运行: ./scripts/build.sh"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 构建产物检查通过${NC}"
}

# 创建备份
create_backup() {
    echo -e "${YELLOW}💾 创建应用备份...${NC}"
    
    BACKUP_NAME="telegramai-backup-$(date +%Y%m%d-%H%M%S)"
    
    ssh $DEPLOY_USER@$DEPLOY_HOST << EOF
        # 创建备份目录
        mkdir -p $BACKUP_DIR
        
        # 停止服务
        sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
        
        # 备份应用文件
        if [ -d "$DEPLOY_PATH" ]; then
            tar -czf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $DEPLOY_PATH .
            echo "备份创建: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
        fi
        
        # 清理旧备份（保留最近5个）
        cd $BACKUP_DIR
        ls -t *.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
EOF
    
    echo -e "${GREEN}✅ 备份创建完成${NC}"
}

# 上传构建产物
upload_artifacts() {
    echo -e "${YELLOW}⬆️  上传构建产物...${NC}"
    
    # 创建临时上传目录
    TEMP_DIR="/tmp/telegramai-deploy-$(date +%s)"
    
    ssh $DEPLOY_USER@$DEPLOY_HOST "mkdir -p $TEMP_DIR"
    
    # 上传文件
    rsync -avz --progress dist/ $DEPLOY_USER@$DEPLOY_HOST:$TEMP_DIR/
    
    echo -e "${GREEN}✅ 文件上传完成${NC}"
}

# 部署应用
deploy_application() {
    echo -e "${YELLOW}🔄 部署应用...${NC}"
    
    ssh $DEPLOY_USER@$DEPLOY_HOST << EOF
        set -e
        
        # 创建部署目录
        sudo mkdir -p $DEPLOY_PATH
        sudo chown $DEPLOY_USER:$DEPLOY_USER $DEPLOY_PATH
        
        # 移动文件到部署目录
        rsync -av $TEMP_DIR/ $DEPLOY_PATH/
        
        # 设置权限
        chmod +x $DEPLOY_PATH/*.AppImage 2>/dev/null || true
        chmod +x $DEPLOY_PATH/TelegramAI 2>/dev/null || true
        
        # 清理临时目录
        rm -rf $TEMP_DIR
        
        echo "应用部署到: $DEPLOY_PATH"
EOF
    
    echo -e "${GREEN}✅ 应用部署完成${NC}"
}

# 配置系统服务
setup_service() {
    echo -e "${YELLOW}⚙️  配置系统服务...${NC}"
    
    ssh $DEPLOY_USER@$DEPLOY_HOST << 'EOF'
        # 创建systemd服务文件
        sudo tee /etc/systemd/system/telegramai.service > /dev/null << EOFSVC
[Unit]
Description=TelegramAI Service
After=network.target

[Service]
Type=simple
User=telegramai
WorkingDirectory=/opt/telegramai
ExecStart=/opt/telegramai/TelegramAI
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOFSVC
        
        # 重新加载systemd
        sudo systemctl daemon-reload
        sudo systemctl enable telegramai
        
        echo "系统服务配置完成"
EOF
    
    echo -e "${GREEN}✅ 系统服务配置完成${NC}"
}

# 更新配置文件
update_configuration() {
    echo -e "${YELLOW}📝 更新配置文件...${NC}"
    
    ssh $DEPLOY_USER@$DEPLOY_HOST << EOF
        cd $DEPLOY_PATH
        
        # 备份现有配置
        if [ -f ".env" ]; then
            cp .env .env.backup
        fi
        
        # 如果没有配置文件，从示例创建
        if [ ! -f ".env" ] && [ -f ".env.example" ]; then
            cp .env.example .env
            echo "已创建配置文件，请编辑 $DEPLOY_PATH/.env"
        fi
        
        # 创建必要目录
        mkdir -p data/sessions data/backups data/cache logs
        
        # 设置权限
        chmod 600 .env 2>/dev/null || true
        chmod -R 755 data logs
EOF
    
    echo -e "${GREEN}✅ 配置文件更新完成${NC}"
}

# 启动服务
start_service() {
    echo -e "${YELLOW}▶️  启动服务...${NC}"
    
    ssh $DEPLOY_USER@$DEPLOY_HOST << EOF
        # 启动服务
        sudo systemctl start $SERVICE_NAME
        
        # 等待服务启动
        sleep 5
        
        # 检查服务状态
        if sudo systemctl is-active $SERVICE_NAME >/dev/null 2>&1; then
            echo "✅ 服务启动成功"
            sudo systemctl status $SERVICE_NAME --no-pager -l
        else
            echo "❌ 服务启动失败"
            sudo journalctl -u $SERVICE_NAME --no-pager -l -n 20
            exit 1
        fi
EOF
    
    echo -e "${GREEN}✅ 服务启动成功${NC}"
}

# 健康检查
health_check() {
    echo -e "${YELLOW}🔍 执行健康检查...${NC}"
    
    # 等待服务完全启动
    sleep 10
    
    ssh $DEPLOY_USER@$DEPLOY_HOST << EOF
        # 检查进程
        if pgrep -f "TelegramAI" >/dev/null; then
            echo "✅ 进程运行正常"
        else
            echo "❌ 进程未运行"
            exit 1
        fi
        
        # 检查端口
        if ss -tuln | grep -q ":8000"; then
            echo "✅ 端口8000监听正常"
        else
            echo "⚠️  端口8000未监听"
        fi
        
        # 检查日志
        if [ -f "$DEPLOY_PATH/logs/telegram_ai.log" ]; then
            echo "✅ 日志文件存在"
            echo "最近日志:"
            tail -n 5 $DEPLOY_PATH/logs/telegram_ai.log
        else
            echo "⚠️  日志文件不存在"
        fi
EOF
    
    echo -e "${GREEN}✅ 健康检查完成${NC}"
}

# 回滚部署
rollback_deployment() {
    echo -e "${YELLOW}⏪ 回滚部署...${NC}"
    
    # 获取最新备份
    LATEST_BACKUP=$(ssh $DEPLOY_USER@$DEPLOY_HOST "ls -t $BACKUP_DIR/*.tar.gz 2>/dev/null | head -n 1" || echo "")
    
    if [ -z "$LATEST_BACKUP" ]; then
        echo -e "${RED}❌ 没有找到可用的备份${NC}"
        exit 1
    fi
    
    ssh $DEPLOY_USER@$DEPLOY_HOST << EOF
        # 停止服务
        sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
        
        # 清除当前部署
        rm -rf $DEPLOY_PATH/*
        
        # 恢复备份
        tar -xzf $LATEST_BACKUP -C $DEPLOY_PATH
        
        # 重启服务
        sudo systemctl start $SERVICE_NAME
        
        echo "回滚到备份: $LATEST_BACKUP"
EOF
    
    echo -e "${GREEN}✅ 回滚完成${NC}"
}

# 显示部署摘要
show_summary() {
    echo ""
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo -e "${BLUE}部署摘要:${NC}"
    echo -e "  版本: ${GREEN}$VERSION${NC}"
    echo -e "  目标: ${GREEN}$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH${NC}"
    echo -e "  服务: ${GREEN}$SERVICE_NAME${NC}"
    echo -e "  部署时间: ${GREEN}$(date)${NC}"
    echo ""
    echo -e "${BLUE}管理命令:${NC}"
    echo -e "  查看状态: ${YELLOW}sudo systemctl status $SERVICE_NAME${NC}"
    echo -e "  查看日志: ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
    echo -e "  重启服务: ${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}"
    echo ""
    echo -e "${BLUE}配置文件:${NC}"
    echo -e "  环境配置: ${YELLOW}$DEPLOY_PATH/.env${NC}"
    echo -e "  数据目录: ${YELLOW}$DEPLOY_PATH/data${NC}"
    echo -e "  日志目录: ${YELLOW}$DEPLOY_PATH/logs${NC}"
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
    echo -e "${BLUE}TelegramAI 部署系统${NC}"
    echo ""
    
    check_ssh_connection
    check_build_artifacts
    create_backup
    upload_artifacts
    deploy_application
    setup_service
    update_configuration
    start_service
    health_check
    show_summary
}

# 脚本参数处理
case "${1:-}" in
    "--help"|"-h")
        echo "用法: $0 [选项] [版本]"
        echo ""
        echo "选项:"
        echo "  --rollback    回滚到上一个版本"
        echo "  --check       仅执行健康检查"
        echo "  --config      仅更新配置"
        echo "  --help        显示此帮助信息"
        echo ""
        echo "环境变量:"
        echo "  DEPLOY_USER   部署用户 (默认: telegramai)"
        echo "  DEPLOY_HOST   目标主机 (默认: localhost)"
        echo "  DEPLOY_PATH   部署路径 (默认: /opt/telegramai)"
        echo "  SERVICE_NAME  服务名称 (默认: telegramai)"
        echo ""
        echo "示例:"
        echo "  $0                    # 部署当前版本"
        echo "  $0 v1.2.0            # 部署指定版本"
        echo "  $0 --rollback        # 回滚部署"
        echo "  DEPLOY_HOST=prod.example.com $0  # 部署到指定服务器"
        exit 0
        ;;
    "--rollback")
        rollback_deployment
        exit 0
        ;;
    "--check")
        health_check
        exit 0
        ;;
    "--config")
        update_configuration
        exit 0
        ;;
    *)
        main
        ;;
esac