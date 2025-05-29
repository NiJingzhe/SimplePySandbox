#!/bin/bash

# SimplePySandbox 测试脚本
# 使用新的测试结构运行各种类型的测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo "SimplePySandbox 测试脚本"
    echo ""
    echo "用法: $0 [选项] [测试类型]"
    echo ""
    echo "测试类型:"
    echo "  all          - 运行所有测试 (默认)"
    echo "  unit         - 只运行单元测试"
    echo "  integration  - 只运行集成测试"
    echo "  system       - 只运行系统测试"
    echo "  performance  - 只运行性能测试"
    echo "  quick        - 运行快速测试 (排除慢速测试)"
    echo "  slow         - 只运行慢速测试"
    echo "  docker       - 只运行需要Docker的测试"
    echo ""
    echo "选项:"
    echo "  -h, --help   - 显示此帮助信息"
    echo "  -v, --verbose - 详细输出"
    echo "  -c, --coverage - 生成覆盖率报告"
    echo "  --no-setup   - 跳过环境设置"
    echo ""
    echo "示例:"
    echo "  $0 unit               # 运行单元测试"
    echo "  $0 -v integration     # 详细输出运行集成测试"
    echo "  $0 -c all             # 运行所有测试并生成覆盖率报告"
}

# 激活虚拟环境
# 激活虚拟环境
activate_venv() {
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        log_info "虚拟环境已激活"
    else
        log_warning "未找到虚拟环境，使用系统Python"
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查pytest
    if ! python -c "import pytest" &> /dev/null; then
        log_error "pytest 未安装，请运行: pip install pytest"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 运行测试
run_tests() {
    local test_type="$1"
    local verbose="$2"
    local coverage="$3"
    
    log_info "运行 $test_type 测试..."
    
    # 设置环境
    activate_venv
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    # 构建pytest命令
    local cmd="python run_tests.py $test_type"
    
    if [ "$verbose" = "true" ]; then
        cmd="$cmd -v"
    fi
    
    if [ "$coverage" = "true" ]; then
        cmd="$cmd -c"
    fi
    
    log_info "执行命令: $cmd"
    
    # 运行测试
    if eval $cmd; then
        log_success "$test_type 测试通过!"
        return 0
    else
        log_error "$test_type 测试失败!"
        return 1
    fi
}

# 检查服务状态
check_service() {
    log_info "检查服务状态..."
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "服务正在运行"
        return 0
    else
        log_warning "服务未运行，某些集成测试可能会失败"
        log_info "要启动服务，请运行: ./start.sh dev"
        return 1
    fi
}

# 环境设置
setup_environment() {
    log_info "设置测试环境..."
    
    # 创建必要的目录
    mkdir -p tests/reports
    mkdir -p tests/coverage
    
    # 设置权限
    chmod +x run_tests.py
    
    log_success "环境设置完成"
}

# 清理函数
cleanup() {
    log_info "清理测试环境..."
    
    # 清理临时文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "清理完成"
}

# 主函数
main() {
    local test_type="all"
    local verbose="false"
    local coverage="false"
    local no_setup="false"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                verbose="true"
                shift
                ;;
            -c|--coverage)
                coverage="true"
                shift
                ;;
            --no-setup)
                no_setup="true"
                shift
                ;;
            all|unit|integration|system|performance|quick|slow|docker)
                test_type="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "=== SimplePySandbox 测试套件 ==="
    log_info "测试类型: $test_type"
    
    # 设置陷阱以确保清理
    trap cleanup EXIT
    
    # 环境设置
    if [ "$no_setup" != "true" ]; then
        setup_environment
        check_dependencies
    fi
    
    # 检查服务状态（对于需要服务的测试）
    if [[ "$test_type" =~ ^(all|integration|system)$ ]]; then
        check_service
    fi
    
    # 运行测试
    if run_tests "$test_type" "$verbose" "$coverage"; then
        log_success "=== 所有测试完成 ==="
        exit 0
    else
        log_error "=== 测试失败 ==="
        exit 1
    fi
}

# 如果直接运行此脚本，则调用main函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
    
    # 检查服务是否运行
    if ! curl -s http://localhost:8000/health > /dev/null; then
        log_warning "服务未运行，尝试启动服务..."
        # 在后台启动服务
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
        SERVER_PID=$!
        log_info "服务PID: $SERVER_PID"
        
        # 等待服务启动
        log_info "等待服务启动..."
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null; then
                log_success "服务启动成功"
                break
            fi
            sleep 1
        done
        
        if ! curl -s http://localhost:8000/health > /dev/null; then
            log_error "服务启动失败"
            if [ ! -z "$SERVER_PID" ]; then
                kill $SERVER_PID 2>/dev/null || true
            fi
            exit 1
        fi
    fi
    
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    pytest test_main.py -v --tb=short
    
    # 如果我们启动了服务，关闭它
    if [ ! -z "$SERVER_PID" ]; then
        log_info "关闭测试服务..."
        kill $SERVER_PID 2>/dev/null || true
    fi
}

# 运行所有测试
run_all_tests() {
    log_info "运行所有测试..."
    activate_venv
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    # 先运行单元测试
    pytest test_security.py test_utils.py -v --tb=short --cov=sandbox --cov-report=html --cov-report=term
    
    # 然后运行集成测试
    run_integration_tests
}

# 运行性能测试
run_performance_tests() {
    log_info "运行性能测试..."
    activate_venv
    
    # 检查服务是否运行
    if ! curl -s http://localhost:8000/health > /dev/null; then
        log_error "服务未运行，请先启动服务"
        exit 1
    fi
    
    log_info "运行客户端示例测试..."
    python3 examples/client_example.py
    
    log_info "运行高级示例测试..."
    python3 examples/advanced_example.py
}

# 代码质量检查
run_code_quality() {
    log_info "运行代码质量检查..."
    
    # 检查是否安装了工具
    if ! command -v flake8 &> /dev/null; then
        log_warning "flake8 未安装，跳过代码风格检查"
    else
        log_info "检查代码风格..."
        flake8 --max-line-length=100 --ignore=E501,W503 .
        log_success "代码风格检查通过"
    fi
    
    if ! command -v mypy &> /dev/null; then
        log_warning "mypy 未安装，跳过类型检查"
    else
        log_info "检查类型注解..."
        mypy . --ignore-missing-imports
        log_success "类型检查通过"
    fi
}

# 安全检查
run_security_check() {
    log_info "运行安全检查..."
    
    if ! command -v bandit &> /dev/null; then
        log_warning "bandit 未安装，跳过安全检查"
        return
    fi
    
    bandit -r . -x test_*.py,examples/
    log_success "安全检查通过"
}

# Docker测试
run_docker_tests() {
    log_info "运行Docker测试..."
    
    # 构建镜像
    log_info "构建测试镜像..."
    docker build -t python-sandbox-test .
    
    # 运行容器测试
    log_info "测试容器启动..."
    container_id=$(docker run -d -p 8001:8000 python-sandbox-test)
    
    sleep 10
    
    # 健康检查
    if curl -s http://localhost:8001/health > /dev/null; then
        log_success "容器健康检查通过"
    else
        log_error "容器健康检查失败"
        docker logs $container_id
        docker stop $container_id
        exit 1
    fi
    
    # 停止容器
    docker stop $container_id
    log_success "Docker测试完成"
}

# 生成测试报告
generate_report() {
    log_info "生成测试报告..."
    activate_venv
    
    mkdir -p reports
    
    # 生成覆盖率报告
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    pytest --cov=sandbox --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml
    
    # 生成测试报告
    pytest --junitxml=reports/test-results.xml
    
    log_success "测试报告已生成到 reports/ 目录"
}

# 压力测试
run_stress_tests() {
    log_info "运行压力测试..."
    activate_venv
    
    # 检查服务是否运行
    if ! curl -s http://localhost:8000/health > /dev/null; then
        log_error "服务未运行，请先启动服务"
        exit 1
    fi
    
    log_info "开始压力测试（并发请求）..."
    
    # 创建临时测试脚本
    cat > /tmp/stress_test.py << 'EOF'
import requests
import concurrent.futures
import time
import json

def execute_request(i):
    try:
        response = requests.post(
            "http://localhost:8000/execute",
            json={
                "code": f"print(f'Request {i}: Hello from stress test!')",
                "timeout": 10
            },
            timeout=15
        )
        return response.status_code == 200
    except:
        return False

# 并发测试
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(execute_request, i) for i in range(50)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

success_rate = sum(results) / len(results) * 100
print(f"压力测试完成: {sum(results)}/{len(results)} 成功 ({success_rate:.1f}%)")
EOF
    
    python3 /tmp/stress_test.py
    rm /tmp/stress_test.py
    
    log_success "压力测试完成"
}

# 显示帮助
show_help() {
    echo "SimplePySandbox 测试脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  unit          运行单元测试"
    echo "  integration   运行集成测试"
    echo "  all           运行所有测试 (默认)"
    echo "  performance   运行性能测试"
    echo "  quality       代码质量检查"
    echo "  security      安全检查"
    echo "  docker        Docker测试"
    echo "  stress        压力测试"
    echo "  report        生成测试报告"
    echo "  help          显示此帮助"
    echo ""
    echo "示例:"
    echo "  $0 all         # 运行所有测试"
    echo "  $0 unit        # 只运行单元测试"
    echo "  $0 performance # 运行性能测试"
}

# 主函数
main() {
    local command=${1:-all}
    
    case $command in
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "all")
            run_unit_tests
            run_integration_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "quality")
            run_code_quality
            ;;
        "security")
            run_security_check
            ;;
        "docker")
            run_docker_tests
            ;;
        "stress")
            run_stress_tests
            ;;
        "report")
            generate_report
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

main "$@"