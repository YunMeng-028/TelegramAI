# 部署指南

## 概述

本文档详细说明了如何在不同环境中部署TelegramAI应用程序。

## 系统要求

### 最低要求
- **操作系统**: Windows 10/11 (64位), macOS 10.15+, Ubuntu 18.04+
- **内存**: 4GB RAM
- **磁盘空间**: 2GB可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Windows 11, macOS 12+, Ubuntu 20.04+
- **内存**: 8GB RAM或更多
- **磁盘空间**: 10GB可用空间
- **CPU**: 4核心或更多

## 预构建安装包部署

### Windows部署

1. **下载安装包**
   ```
   从GitHub Releases下载最新的Windows安装包(.exe)
   ```

2. **运行安装程序**
   - 双击下载的.exe文件
   - 按照安装向导进行安装
   - 选择安装目录（默认: `C:\Program Files\TelegramAI`）

3. **首次启动配置**
   - 启动TelegramAI应用
   - 输入授权密钥
   - 配置基本设置

### macOS部署

1. **下载安装包**
   ```
   从GitHub Releases下载最新的macOS安装包(.dmg)
   ```

2. **安装应用**
   - 双击.dmg文件
   - 将TelegramAI拖拽到Applications文件夹
   - 首次启动时允许安全警告

3. **授权设置**
   - 系统偏好设置 → 安全性与隐私
   - 允许TelegramAI运行

### Linux部署

1. **使用AppImage**
   ```bash
   # 下载AppImage
   wget https://github.com/telegramai/TelegramAI/releases/latest/download/TelegramAI.AppImage
   
   # 添加执行权限
   chmod +x TelegramAI.AppImage
   
   # 运行
   ./TelegramAI.AppImage
   ```

2. **使用DEB包（Ubuntu/Debian）**
   ```bash
   # 下载deb包
   wget https://github.com/telegramai/TelegramAI/releases/latest/download/telegramai_1.0.0_amd64.deb
   
   # 安装
   sudo dpkg -i telegramai_1.0.0_amd64.deb
   
   # 修复依赖（如果需要）
   sudo apt-get install -f
   ```

## 源码部署

### 环境准备

1. **安装Node.js**
   ```bash
   # 使用nvm安装Node.js 22.x
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 22
   nvm use 22
   ```

2. **安装Python**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3.12 python3.12-venv python3.12-dev
   
   # macOS (使用Homebrew)
   brew install python@3.12
   
   # Windows (使用Chocolatey)
   choco install python --version=3.12
   ```

3. **安装Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

### 源码构建

1. **克隆仓库**
   ```bash
   git clone https://github.com/telegramai/TelegramAI.git
   cd TelegramAI
   ```

2. **安装依赖**
   ```bash
   # Python依赖
   poetry install
   
   # Node.js依赖
   npm install
   ```

3. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.example .env
   
   # 编辑配置文件
   nano .env
   ```

4. **构建应用**
   ```bash
   # 构建前端
   npm run build
   
   # 打包Electron应用
   npm run dist
   ```

## 生产环境部署

### 服务器部署

1. **创建专用用户**
   ```bash
   sudo useradd -m -s /bin/bash telegramai
   sudo usermod -aG sudo telegramai
   ```

2. **安装到系统目录**
   ```bash
   sudo mkdir -p /opt/telegramai
   sudo chown telegramai:telegramai /opt/telegramai
   
   # 复制构建产物
   sudo cp -r dist/* /opt/telegramai/
   ```

3. **创建systemd服务**
   ```bash
   sudo tee /etc/systemd/system/telegramai.service << EOF
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
   
   [Install]
   WantedBy=multi-user.target
   EOF
   ```

4. **启动服务**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegramai
   sudo systemctl start telegramai
   ```

### Docker部署

1. **创建Dockerfile**
   ```dockerfile
   FROM node:22-alpine AS frontend-builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY . .
   RUN npm run build
   
   FROM python:3.12-slim AS backend-builder
   WORKDIR /app
   RUN pip install poetry
   COPY pyproject.toml poetry.lock ./
   RUN poetry config virtualenvs.create false && poetry install --no-dev
   
   FROM ubuntu:22.04
   RUN apt-get update && apt-get install -y \
       python3.12 \
       python3-pip \
       xvfb \
       libgtk-3-0 \
       libgbm1 \
       libnss3 \
       libasound2 \
       && rm -rf /var/lib/apt/lists/*
   
   WORKDIR /app
   COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
   COPY --from=frontend-builder /app/dist ./dist
   COPY backend ./backend
   
   EXPOSE 8000
   CMD ["python3", "backend/main.py"]
   ```

2. **构建镜像**
   ```bash
   docker build -t telegramai:latest .
   ```

3. **运行容器**
   ```bash
   docker run -d \
     --name telegramai \
     -p 8000:8000 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     --env-file .env \
     telegramai:latest
   ```

### Docker Compose部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  telegramai:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - telegramai
    restart: unless-stopped
```

## 配置管理

### 环境变量配置

生产环境推荐的环境变量：

```bash
# 基础配置
NODE_ENV=production
DEBUG=false
LOG_LEVEL=info

# API配置
OPENAI_API_KEY=your_production_key
ANTHROPIC_API_KEY=your_production_key
CLAUDE_CODE_API_KEY=your_production_key

# 数据库配置
DATABASE_PATH=/app/data/telegram_ai.db
DATABASE_BACKUP_PATH=/app/data/backups

# 安全配置
SECRET_KEY=your_very_secure_secret_key
ENCRYPTION_KEY=your_encryption_key_here

# 性能配置
MAX_WORKERS=10
MAX_CONNECTIONS=200
CACHE_TTL=7200

# 监控配置
ENABLE_METRICS=true
SENTRY_DSN=your_sentry_dsn
```

### SSL/TLS配置

1. **生成SSL证书**
   ```bash
   # 自签名证书（开发环境）
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   
   # Let's Encrypt证书（生产环境）
   certbot certonly --standalone -d your-domain.com
   ```

2. **Nginx配置**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /etc/nginx/ssl/cert.pem;
       ssl_certificate_key /etc/nginx/ssl/key.pem;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## 监控与日志

### 日志配置

1. **日志轮转**
   ```bash
   # /etc/logrotate.d/telegramai
   /opt/telegramai/logs/*.log {
       daily
       missingok
       rotate 30
       compress
       delaycompress
       notifempty
       copytruncate
   }
   ```

2. **集中化日志**
   ```yaml
   # docker-compose.yml (添加日志服务)
   fluentd:
     image: fluentd:latest
     volumes:
       - ./fluentd:/fluentd/etc
       - ./logs:/var/log/telegramai
     ports:
       - "24224:24224"
   ```

### 监控配置

1. **Prometheus配置**
   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'telegramai'
       static_configs:
         - targets: ['localhost:9090']
   ```

2. **Grafana仪表板**
   - 导入预配置的仪表板模板
   - 监控关键指标：CPU、内存、响应时间、错误率

## 备份与恢复

### 数据备份

1. **自动备份脚本**
   ```bash
   #!/bin/bash
   # backup.sh
   
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/app/data/backups"
   
   # 创建备份目录
   mkdir -p $BACKUP_DIR
   
   # 备份数据库
   sqlite3 /app/data/telegram_ai.db ".backup $BACKUP_DIR/telegram_ai_$DATE.db"
   
   # 备份配置文件
   tar -czf $BACKUP_DIR/config_$DATE.tar.gz /app/config
   
   # 清理30天前的备份
   find $BACKUP_DIR -name "*.db" -mtime +30 -delete
   find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
   ```

2. **定时备份**
   ```bash
   # 添加到crontab
   crontab -e
   
   # 每天凌晨2点备份
   0 2 * * * /opt/telegramai/scripts/backup.sh
   ```

### 灾难恢复

1. **数据恢复**
   ```bash
   # 停止服务
   sudo systemctl stop telegramai
   
   # 恢复数据库
   cp /app/data/backups/telegram_ai_20240115_020000.db /app/data/telegram_ai.db
   
   # 恢复配置
   tar -xzf /app/data/backups/config_20240115_020000.tar.gz -C /
   
   # 重启服务
   sudo systemctl start telegramai
   ```

## 性能优化

### 系统优化

1. **内核参数调优**
   ```bash
   # /etc/sysctl.conf
   net.core.somaxconn = 65535
   net.ipv4.tcp_max_syn_backlog = 65535
   net.ipv4.ip_local_port_range = 1024 65535
   fs.file-max = 100000
   ```

2. **用户限制调整**
   ```bash
   # /etc/security/limits.conf
   telegramai soft nofile 100000
   telegramai hard nofile 100000
   telegramai soft nproc 32768
   telegramai hard nproc 32768
   ```

### 应用优化

1. **数据库优化**
   ```sql
   PRAGMA journal_mode = WAL;
   PRAGMA synchronous = NORMAL;
   PRAGMA cache_size = 10000;
   PRAGMA temp_store = MEMORY;
   ```

2. **缓存策略**
   - Redis缓存热点数据
   - 内存缓存常用配置
   - CDN加速静态资源

## 故障排除

### 常见问题

1. **应用启动失败**
   ```bash
   # 检查日志
   journalctl -u telegramai -f
   
   # 检查端口占用
   netstat -tlnp | grep :8000
   
   # 检查权限
   ls -la /opt/telegramai/
   ```

2. **数据库错误**
   ```bash
   # 检查数据库文件
   sqlite3 /app/data/telegram_ai.db ".schema"
   
   # 修复数据库
   sqlite3 /app/data/telegram_ai.db ".recover"
   ```

3. **内存不足**
   ```bash
   # 检查内存使用
   free -h
   ps aux --sort=-%mem | head
   
   # 调整Swap
   sudo swapon --show
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 安全加固

### 系统安全

1. **防火墙配置**
   ```bash
   sudo ufw enable
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 8000/tcp  # 仅内部访问
   ```

2. **用户权限控制**
   ```bash
   # 最小权限原则
   sudo chmod 750 /opt/telegramai
   sudo chown -R telegramai:telegramai /opt/telegramai
   ```

### 应用安全

1. **API安全**
   - 启用速率限制
   - 使用HTTPS
   - 验证输入参数
   - 定期轮换密钥

2. **数据安全**
   - 加密敏感数据
   - 定期备份
   - 访问控制
   - 审计日志

## 升级指南

### 应用升级

1. **备份数据**
   ```bash
   /opt/telegramai/scripts/backup.sh
   ```

2. **下载新版本**
   ```bash
   wget https://github.com/telegramai/TelegramAI/releases/latest/download/telegramai-linux.tar.gz
   ```

3. **更新应用**
   ```bash
   sudo systemctl stop telegramai
   tar -xzf telegramai-linux.tar.gz -C /opt/telegramai
   sudo systemctl start telegramai
   ```

4. **验证升级**
   ```bash
   curl http://localhost:8000/health
   ```

## 支持与联系

如需部署支持，请联系：
- 技术支持：support@telegramai.com
- 部署文档：https://docs.telegramai.com/deployment
- 社区论坛：https://community.telegramai.com