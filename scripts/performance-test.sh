#!/bin/bash

# TelegramAI 性能测试脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPORT_DIR="performance-reports"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

echo -e "${BLUE}⚡ TelegramAI 性能测试套件${NC}"
echo -e "${BLUE}时间戳: ${GREEN}$TIMESTAMP${NC}"
echo ""

# 创建报告目录
mkdir -p $REPORT_DIR

# 前端性能测试
test_frontend_performance() {
    echo -e "${YELLOW}🎨 前端性能测试...${NC}"
    
    # 检查开发服务器是否运行
    if ! curl -s http://localhost:5173 >/dev/null; then
        echo -e "${YELLOW}启动开发服务器...${NC}"
        npm run dev &
        DEV_PID=$!
        sleep 10
    fi
    
    # Bundle大小分析
    echo -e "${BLUE}分析Bundle大小...${NC}"
    npm run build -- --mode=analyze
    
    # Lighthouse性能测试
    if command -v lighthouse &> /dev/null; then
        echo -e "${BLUE}运行Lighthouse测试...${NC}"
        lighthouse http://localhost:5173 \
            --output=html \
            --output-path=$REPORT_DIR/lighthouse-$TIMESTAMP.html \
            --chrome-flags="--headless --no-sandbox" \
            --quiet
    else
        echo -e "${YELLOW}⚠️  Lighthouse未安装，跳过测试${NC}"
    fi
    
    # 停止开发服务器
    if [ ! -z "$DEV_PID" ]; then
        kill $DEV_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ 前端性能测试完成${NC}"
}

# 后端性能测试
test_backend_performance() {
    echo -e "${YELLOW}🐍 后端性能测试...${NC}"
    
    # 检查后端服务器是否运行
    if ! curl -s http://localhost:8000/health >/dev/null; then
        echo -e "${YELLOW}启动后端服务器...${NC}"
        poetry run python backend/main.py &
        BACKEND_PID=$!
        sleep 10
    fi
    
    # API响应时间测试
    echo -e "${BLUE}测试API响应时间...${NC}"
    
    # 使用curl测试各个端点
    endpoints=(
        "/health"
        "/api/v1/system/status"
    )
    
    for endpoint in "${endpoints[@]}"; do
        echo -e "${BLUE}测试端点: $endpoint${NC}"
        
        # 测试10次并计算平均响应时间
        total_time=0
        success_count=0
        
        for i in {1..10}; do
            response_time=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:8000$endpoint 2>/dev/null || echo "0")
            if [ "$response_time" != "0" ]; then
                total_time=$(echo "$total_time + $response_time" | bc -l 2>/dev/null || echo "$total_time")
                ((success_count++))
            fi
        done
        
        if [ $success_count -gt 0 ]; then
            avg_time=$(echo "scale=3; $total_time / $success_count" | bc -l 2>/dev/null || echo "0")
            echo -e "  平均响应时间: ${GREEN}${avg_time}s${NC} (成功: $success_count/10)"
        else
            echo -e "  ${RED}❌ 端点无响应${NC}"
        fi
    done
    
    # 压力测试
    if command -v ab &> /dev/null; then
        echo -e "${BLUE}运行压力测试...${NC}"
        ab -n 100 -c 10 -g $REPORT_DIR/ab-results-$TIMESTAMP.dat http://localhost:8000/health > $REPORT_DIR/ab-report-$TIMESTAMP.txt
        echo -e "${GREEN}✅ 压力测试完成，报告: $REPORT_DIR/ab-report-$TIMESTAMP.txt${NC}"
    else
        echo -e "${YELLOW}⚠️  Apache Bench未安装，跳过压力测试${NC}"
    fi
    
    # 停止后端服务器
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ 后端性能测试完成${NC}"
}

# 内存使用分析
test_memory_usage() {
    echo -e "${YELLOW}🧠 内存使用分析...${NC}"
    
    # Python内存分析
    echo -e "${BLUE}Python内存分析...${NC}"
    if command -v memory_profiler &> /dev/null; then
        poetry run python -m memory_profiler backend/main.py > $REPORT_DIR/memory-python-$TIMESTAMP.txt &
        MEMORY_PID=$!
        sleep 30
        kill $MEMORY_PID 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠️  memory_profiler未安装，跳过Python内存分析${NC}"
    fi
    
    # Node.js内存分析
    echo -e "${BLUE}Node.js内存分析...${NC}"
    if command -v clinic &> /dev/null; then
        npm run build
        clinic doctor --dest $REPORT_DIR/clinic-$TIMESTAMP -- node dist/main.js &
        CLINIC_PID=$!
        sleep 30
        kill $CLINIC_PID 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠️  clinic未安装，跳过Node.js内存分析${NC}"
    fi
    
    echo -e "${GREEN}✅ 内存使用分析完成${NC}"
}

# 数据库性能测试
test_database_performance() {
    echo -e "${YELLOW}🗄️  数据库性能测试...${NC}"
    
    # SQLite性能测试
    if [ -f "data/telegram_ai.db" ]; then
        echo -e "${BLUE}SQLite查询性能测试...${NC}"
        
        # 创建测试脚本
        cat > /tmp/db_perf_test.py << 'EOF'
import sqlite3
import time
import statistics

def test_query_performance():
    conn = sqlite3.connect('data/telegram_ai.db')
    cursor = conn.cursor()
    
    # 测试查询
    queries = [
        "SELECT COUNT(*) FROM accounts",
        "SELECT COUNT(*) FROM targets", 
        "SELECT COUNT(*) FROM interactions"
    ]
    
    results = {}
    
    for query in queries:
        times = []
        for _ in range(10):
            start = time.time()
            try:
                cursor.execute(query)
                cursor.fetchall()
                end = time.time()
                times.append(end - start)
            except:
                times.append(float('inf'))
        
        if times and all(t != float('inf') for t in times):
            avg_time = statistics.mean(times)
            results[query] = avg_time
            print(f"{query}: {avg_time:.4f}s")
        else:
            print(f"{query}: 查询失败")
    
    conn.close()
    return results

if __name__ == "__main__":
    test_query_performance()
EOF
        
        poetry run python /tmp/db_perf_test.py > $REPORT_DIR/database-$TIMESTAMP.txt
        rm /tmp/db_perf_test.py
        
        echo -e "${GREEN}✅ 数据库性能测试完成${NC}"
    else
        echo -e "${YELLOW}⚠️  数据库文件不存在，跳过测试${NC}"
    fi
}

# 生成性能报告
generate_performance_report() {
    echo -e "${YELLOW}📊 生成性能报告...${NC}"
    
    REPORT_FILE="$REPORT_DIR/performance-summary-$TIMESTAMP.md"
    
    cat > $REPORT_FILE << EOF
# TelegramAI 性能测试报告

**测试时间**: $(date)
**版本**: $(git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
**提交**: $(git rev-parse HEAD 2>/dev/null || echo "unknown")

## 测试环境

- **操作系统**: $(uname -s) $(uname -r)
- **Node.js版本**: $(node --version)
- **Python版本**: $(python3 --version)
- **内存**: $(free -h | grep "Mem:" | awk '{print $2}' 2>/dev/null || echo "unknown")
- **CPU**: $(nproc 2>/dev/null || echo "unknown") 核心

## 测试结果

### 前端性能

- Bundle大小: 查看 dist/stats.html
- Lighthouse报告: lighthouse-$TIMESTAMP.html

### 后端性能

- API响应时间: 查看 ab-report-$TIMESTAMP.txt
- 内存使用: 查看 memory-python-$TIMESTAMP.txt

### 数据库性能

- 查询性能: 查看 database-$TIMESTAMP.txt

## 建议

1. **Bundle优化**: 检查是否有不必要的依赖
2. **API性能**: 关注响应时间超过1秒的端点
3. **内存使用**: 监控内存泄漏和峰值使用
4. **数据库**: 添加必要的索引优化查询

## 文件清单

EOF
    
    # 列出所有生成的报告文件
    ls -la $REPORT_DIR/*$TIMESTAMP* >> $REPORT_FILE 2>/dev/null || true
    
    echo -e "${GREEN}✅ 性能报告生成完成: $REPORT_FILE${NC}"
}

# 清理旧报告
cleanup_old_reports() {
    echo -e "${YELLOW}🧹 清理旧报告...${NC}"
    
    # 保留最近30天的报告
    find $REPORT_DIR -name "*" -type f -mtime +30 -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 显示测试摘要
show_summary() {
    echo ""
    echo -e "${GREEN}🎉 性能测试完成！${NC}"
    echo -e "${BLUE}测试摘要:${NC}"
    echo -e "  时间戳: ${GREEN}$TIMESTAMP${NC}"
    echo -e "  报告目录: ${GREEN}$REPORT_DIR${NC}"
    echo ""
    
    if [ -d "$REPORT_DIR" ]; then
        echo -e "${BLUE}生成的报告:${NC}"
        ls -la $REPORT_DIR/*$TIMESTAMP* 2>/dev/null || echo "无报告文件"
    fi
    
    echo ""
    echo -e "${BLUE}查看报告:${NC}"
    echo -e "  性能摘要: ${YELLOW}cat $REPORT_DIR/performance-summary-$TIMESTAMP.md${NC}"
    if [ -f "$REPORT_DIR/lighthouse-$TIMESTAMP.html" ]; then
        echo -e "  Lighthouse: ${YELLOW}open $REPORT_DIR/lighthouse-$TIMESTAMP.html${NC}"
    fi
}

# 主函数
main() {
    echo -e "${GREEN}"
    echo "██████╗ ███████╗██████╗ ███████╗ ██████╗ ██████╗ ███╗   ███╗ █████╗ ███╗   ██╗ ██████╗███████╗"
    echo "██╔══██╗██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗████╗ ████║██╔══██╗████╗  ██║██╔════╝██╔════╝"
    echo "██████╔╝█████╗  ██████╔╝█████╗  ██║   ██║██████╔╝██╔████╔██║███████║██╔██╗ ██║██║     █████╗"
    echo "██╔═══╝ ██╔══╝  ██╔══██╗██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║██╔══██║██║╚██╗██║██║     ██╔══╝"
    echo "██║     ███████╗██║  ██║██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║██║  ██║██║ ╚████║╚██████╗███████╗"
    echo "╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝"
    echo -e "${NC}"
    echo -e "${BLUE}TelegramAI 性能测试系统${NC}"
    echo ""
    
    cleanup_old_reports
    test_frontend_performance
    test_backend_performance
    test_memory_usage
    test_database_performance
    generate_performance_report
    show_summary
}

# 脚本参数处理
case "${1:-}" in
    "--help"|"-h")
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --frontend    仅测试前端性能"
        echo "  --backend     仅测试后端性能"
        echo "  --memory      仅测试内存使用"
        echo "  --database    仅测试数据库性能"
        echo "  --cleanup     清理旧报告"
        echo "  --help        显示帮助信息"
        echo ""
        echo "报告将保存在 $REPORT_DIR 目录中"
        exit 0
        ;;
    "--frontend")
        test_frontend_performance
        exit 0
        ;;
    "--backend")
        test_backend_performance
        exit 0
        ;;
    "--memory")
        test_memory_usage
        exit 0
        ;;
    "--database")
        test_database_performance
        exit 0
        ;;
    "--cleanup")
        cleanup_old_reports
        exit 0
        ;;
    *)
        main
        ;;
esac