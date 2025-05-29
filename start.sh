#!/bin/bash

# SimplePySandbox 启动脚本

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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行，请启动Docker"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    # 检查虚拟环境
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        log_warning "建议在虚拟环境中运行"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    pip install -r requirements.txt
    log_success "依赖安装完成"
}

# 构建Docker镜像
build_docker() {
    log_info "构建Docker镜像..."
    docker build -t python-sandbox .
    log_success "Docker镜像构建完成"
}

# 启动开发服务器
start_dev() {
    log_info "启动开发服务器..."
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# 启动生产服务器
start_prod() {
    log_info "启动生产服务器..."
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
}

# 使用Docker Compose启动
start_docker() {
    log_info "使用Docker Compose启动..."
    docker-compose up -d
    log_success "服务已启动，访问 http://localhost:8000"
    log_info "查看日志: docker-compose logs -f"
    log_info "停止服务: docker-compose down"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    pytest -v
    log_success "测试完成"
}

# 显示帮助信息
show_help() {
    echo "SimplePySandbox 启动脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  dev       启动开发服务器 (默认)"
    echo "  prod      启动生产服务器"
    echo "  docker    使用Docker Compose启动"
    echo "  build     构建Docker镜像"
    echo "  install   安装依赖"
    echo "  test      运行测试"
    echo "  check     检查依赖"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev      # 启动开发服务器"
    echo "  $0 docker   # 使用Docker启动"
    echo "  $0 test     # 运行测试"
}

# 主函数
main() {
    local command=${1:-dev}
    
    case $command in
        "dev")
            check_dependencies
            install_dependencies
            start_dev
            ;;
        "prod")
            check_dependencies
            install_dependencies
            start_prod
            ;;
        "docker")
            check_dependencies
            build_docker
            start_docker
            ;;
        "build")
            check_dependencies
            build_docker
            ;;
        "install")
            check_dependencies
            install_dependencies
            ;;
        "test")
            check_dependencies
            install_dependencies
            run_tests
            ;;
        "check")
            check_dependencies
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"