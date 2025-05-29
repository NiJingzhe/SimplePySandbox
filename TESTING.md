# SimplePySandbox 测试指南

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 可选：安装开发工具
pip install flake8 mypy bandit coverage
```

### 2. 运行测试

#### 使用测试脚本（推荐）

```bash
# 给脚本执行权限
chmod +x test.sh

# 运行所有测试
./test.sh all

# 运行特定类型的测试
./test.sh unit          # 单元测试
./test.sh integration   # 集成测试
./test.sh performance   # 性能测试
./test.sh quality       # 代码质量检查
./test.sh security      # 安全检查
./test.sh docker        # Docker测试
./test.sh stress        # 压力测试
./test.sh report        # 生成测试报告
```

#### 直接使用pytest

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest test_main.py
pytest test_security.py
pytest test_utils.py

# 运行测试并显示覆盖率
pytest --cov=. --cov-report=html

# 运行测试并生成详细报告
pytest -v --tb=long
```

## 测试类型详解

### 1. 单元测试

测试独立的模块和函数：

```bash
# 运行安全模块测试
pytest test_security.py -v

# 运行工具模块测试
pytest test_utils.py -v
```

**测试内容：**
- 安全策略验证
- 文件名验证
- 输出清理
- 临时目录管理

### 2. 集成测试

测试完整的API功能：

```bash
# 需要先启动服务（在另一个终端）
uvicorn main:app --reload

# 然后运行集成测试
pytest test_main.py -v
```

**测试内容：**
- API端点功能
- 代码执行流程
- 文件处理
- 错误处理

### 3. 性能测试

测试系统性能和并发能力：

```bash
# 确保服务正在运行
./test.sh performance
```

**测试内容：**
- 代码执行速度
- 并发处理能力
- 内存使用情况
- 响应时间

### 4. 压力测试

测试系统在高负载下的表现：

```bash
# 确保服务正在运行
./test.sh stress
```

**测试内容：**
- 高并发请求处理
- 系统稳定性
- 资源限制

## 测试配置

### pytest.ini 配置

```ini
[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### 环境变量

```bash
# 设置Python路径
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Docker相关
export DOCKER_IMAGE="python:3.11-slim"

# 测试超时
export TEST_TIMEOUT=30
```

## 特定测试场景

### 1. 本地开发测试

```bash
# 快速测试（跳过慢速测试）
pytest -m "not slow"

# 只运行单元测试
pytest test_security.py test_utils.py

# 监控模式（文件变更时自动运行）
pytest-watch
```

### 2. CI/CD 测试

```bash
# 完整测试套件
./test.sh all

# 生成报告
./test.sh report

# 检查代码质量
./test.sh quality

# 安全检查
./test.sh security
```

### 3. Docker 环境测试

```bash
# 构建并测试Docker镜像
./test.sh docker

# 或者手动测试
docker build -t python-sandbox-test .
docker run -d -p 8001:8000 python-sandbox-test
curl http://localhost:8001/health
```

## 测试数据和示例

### 1. 客户端示例测试

```bash
# 确保服务运行在8000端口
python examples/client_example.py
```

### 2. 高级功能测试

```bash
# 运行高级示例
python examples/advanced_example.py
```

## 调试测试

### 1. 详细错误信息

```bash
# 显示完整错误堆栈
pytest --tb=long

# 在第一个失败时停止
pytest -x

# 显示本地变量
pytest --tb=long --showlocals
```

### 2. 调试特定测试

```bash
# 运行特定测试方法
pytest test_main.py::test_simple_code_execution -v

# 运行匹配模式的测试
pytest -k "test_file" -v
```

### 3. 输出调试信息

```bash
# 显示print输出
pytest -s

# 显示日志
pytest --log-cli-level=DEBUG
```

## 测试覆盖率

### 1. 生成覆盖率报告

```bash
# HTML报告
pytest --cov=. --cov-report=html

# 终端报告
pytest --cov=. --cov-report=term-missing

# XML报告（CI/CD）
pytest --cov=. --cov-report=xml
```

### 2. 查看覆盖率

```bash
# 打开HTML报告
open htmlcov/index.html

# 或在浏览器中查看
python -m http.server 8080 -d htmlcov
```

## 常见问题

### 1. Docker 连接问题

```bash
# 检查Docker是否运行
docker version

# 检查Docker权限
sudo chmod 666 /var/run/docker.sock
```

### 2. 服务未启动

```bash
# 启动开发服务器
uvicorn main:app --reload --port 8000

# 检查服务状态
curl http://localhost:8000/health
```

### 3. 依赖问题

```bash
# 重新安装依赖
pip install -r requirements.txt --upgrade

# 检查Python路径
echo $PYTHONPATH
```

### 4. 权限问题

```bash
# 给测试脚本执行权限
chmod +x test.sh

# 检查文件权限
ls -la test.sh
```

## 持续集成示例

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: ./test.sh all
      - run: ./test.sh quality
      - run: ./test.sh security
```

### 本地预提交钩子

```bash
# 安装pre-commit
pip install pre-commit

# 设置钩子
pre-commit install

# 手动运行
pre-commit run --all-files
```

## 性能基准

### 预期性能指标

- 简单代码执行: < 100ms
- 文件操作: < 200ms
- JSON处理: < 300ms
- 并发10个请求: 95%成功率
- 内存使用: < 512MB per 容器

### 监控命令

```bash
# 监控资源使用
docker stats

# 监控API性能
time curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"print(\"test\")"}'
```

## 最佳实践

1. **测试前准备**：确保Docker服务运行，端口8000可用
2. **测试隔离**：每个测试使用独立的临时目录
3. **清理资源**：测试后自动清理临时文件和容器
4. **错误处理**：测试各种错误情况和边界条件
5. **性能监控**：定期运行性能测试，监控退化
6. **安全检查**：定期运行安全扫描，确保代码安全
