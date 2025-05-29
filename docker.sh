#!/bin/bash
# SimplePySandbox Docker启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "SimplePySandbox Docker 管理脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  build     构建Docker镜像"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  logs      查看日志"
    echo "  status    查看状态"
    echo "  clean     清理容器和镜像"
    echo "  test      运行测试"
    echo "  help      显示此帮助信息"
    echo ""
    echo "选项:"
    echo "  --build   在启动时重新构建"
    echo "  --dev     开发模式（挂载源代码）"
    echo ""
    echo "示例:"
    echo "  $0 build"
    echo "  $0 start"
    echo "  $0 restart --build"
}

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker未运行，请先启动Docker"
        exit 1
    fi
}

# 使用固定的docker-compose文件
get_compose_file() {
    echo "docker-compose.yml"
}

# 构建镜像
build_image() {
    log_info "构建SimplePySandbox Docker镜像..."
    
    docker build -t simplepysandbox:latest .
    
    if [ $? -eq 0 ]; then
        log_success "镜像构建完成"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_service() {
    local compose_file=$(get_compose_file "$@")
    local build_flag=""
    
    if [[ "$@" == *"--build"* ]]; then
        build_flag="--build"
    fi
    
    log_info "启动SimplePySandbox服务..."
    
    # 创建必要的目录
    mkdir -p data/environments logs
    
    docker-compose -f "$compose_file" up -d $build_flag
    
    if [ $? -eq 0 ]; then
        log_success "服务启动成功"
        log_info "服务地址: http://localhost:8000"
        log_info "API文档: http://localhost:8000/docs"
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 停止服务
stop_service() {
    local compose_file=$(get_compose_file "$@")
    
    log_info "停止SimplePySandbox服务..."
    
    docker-compose -f "$compose_file" down
    
    if [ $? -eq 0 ]; then
        log_success "服务已停止"
    else
        log_error "停止服务失败"
        exit 1
    fi
}

# 重启服务
restart_service() {
    log_info "重启SimplePySandbox服务..."
    stop_service "$@"
    start_service "$@"
}

# 查看日志
show_logs() {
    local compose_file=$(get_compose_file "$@")
    
    log_info "显示服务日志..."
    docker-compose -f "$compose_file" logs -f --tail=100
}

# 查看状态
show_status() {
    local compose_file=$(get_compose_file "$@")
    
    log_info "服务状态:"
    docker-compose -f "$compose_file" ps
    
    echo ""
    log_info "容器详细信息:"
    docker ps | grep simplepysandbox || echo "未找到运行中的容器"
}

# 清理
clean_all() {
    log_warning "这将删除所有SimplePySandbox相关的容器和镜像"
    read -p "确定要继续吗? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        log_info "清理容器..."
        docker-compose down --remove-orphans 2>/dev/null || true
        
        log_info "删除镜像..."
        docker rmi simplepysandbox:latest 2>/dev/null || true
        
        log_info "清理未使用的Docker资源..."
        docker system prune -f
        
        log_success "清理完成"
    else
        log_info "取消清理"
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 检查服务是否运行
    if ! docker ps | grep -q simplepysandbox; then
        log_warning "服务未运行，正在启动..."
        start_service "$@"
        sleep 5
    fi
    
    # 运行测试
    docker exec simplepysandbox python -m pytest tests/ -v
    
    if [ $? -eq 0 ]; then
        log_success "所有测试通过"
    else
        log_error "部分测试失败"
        exit 1
    fi
}

# 主函数
main() {
    check_docker
    
    case "${1:-help}" in
        "build")
            build_image
            ;;
        "start")
            start_service "$@"
            ;;
        "stop")
            stop_service "$@"
            ;;
        "restart")
            restart_service "$@"
            ;;
        "logs")
            show_logs "$@"
            ;;
        "status")
            show_status "$@"
            ;;
        "clean")
            clean_all
            ;;
        "test")
            run_tests "$@"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
