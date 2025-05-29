# SimplePySandbox 测试文档

## 测试结构

测试代码已经重新组织为以下结构：

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest配置和夹具
├── data/                    # 测试数据文件
│   ├── input.txt           # 示例输入文件
│   └── sample_code.py      # 示例代码文件
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_security.py    # 安全策略测试
│   └── test_utils.py       # 工具函数测试
├── integration/             # 集成测试
│   ├── __init__.py
│   ├── test_main.py        # API端点测试
│   ├── test_timeout.py     # 超时机制测试
│   ├── test_api_timeout.py # API超时测试
│   └── test_environment.py # 环境管理测试
├── system/                  # 系统测试
│   ├── __init__.py
│   └── test_complete_system.py # 完整系统测试
└── performance/             # 性能测试
    ├── __init__.py
    └── test_performance.py # 性能基准测试
```

## 测试类型

### 1. 单元测试 (Unit Tests)
- 测试单个函数或类的功能
- 不依赖外部服务
- 运行速度快
- 标记：`@pytest.mark.unit`

### 2. 集成测试 (Integration Tests)
- 测试组件之间的交互
- 可能需要Docker环境
- 测试API端点和服务集成
- 标记：`@pytest.mark.integration`

### 3. 系统测试 (System Tests)
- 端到端的完整系统测试
- 需要完整的服务环境
- 测试真实用户场景
- 标记：`@pytest.mark.system`

### 4. 性能测试 (Performance Tests)
- 测试系统性能和资源使用
- 执行时间较长
- 标记：`@pytest.mark.performance`

## 运行测试

### 使用测试脚本

```bash
# 运行所有测试
./test.sh

# 运行特定类型的测试
./test.sh unit          # 单元测试
./test.sh integration   # 集成测试
./test.sh system        # 系统测试
./test.sh performance   # 性能测试

# 运行快速测试（排除慢速测试）
./test.sh quick

# 运行慢速测试
./test.sh slow

# 运行需要Docker的测试
./test.sh docker

# 详细输出
./test.sh -v unit

# 生成覆盖率报告
./test.sh -c all
```

### 使用Python测试运行器

```bash
# 直接使用Python运行器
python run_tests.py unit -v -c

# 或者使用pytest
pytest tests/unit/ -v
pytest -m "unit" -v
pytest -m "not slow" -v
```

### 使用pytest直接运行

```bash
# 运行所有测试
pytest

# 运行特定目录
pytest tests/unit/
pytest tests/integration/

# 使用标记过滤
pytest -m unit
pytest -m "integration and not slow"
pytest -m "not requires_docker"

# 详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=sandbox --cov=models --cov=config --cov-report=html
```

## 测试标记

项目使用以下pytest标记来分类测试：

- `unit`: 单元测试
- `integration`: 集成测试
- `system`: 系统测试
- `performance`: 性能测试
- `slow`: 执行时间较长的测试
- `requires_docker`: 需要Docker环境的测试

## 测试夹具 (Fixtures)

在 `conftest.py` 中定义了以下测试夹具：

- `project_root`: 项目根目录路径
- `test_data_dir`: 测试数据目录路径
- `temp_dir`: 临时目录（测试后自动清理）
- `sample_code`: 示例代码集合
- `api_base_url`: API基础URL

## 测试数据

测试数据存储在 `tests/data/` 目录中：

- `sample_code.py`: 示例Python代码
- `input.txt`: 示例输入文件

## 持续集成

测试脚本支持CI/CD环境：

```bash
# CI环境运行
./test.sh --no-setup unit    # 跳过环境设置
./test.sh -c all             # 生成覆盖率报告
```

## 覆盖率报告

生成覆盖率报告：

```bash
# HTML报告
./test.sh -c all

# 查看报告
open htmlcov/index.html
```

## 调试测试

```bash
# 运行单个测试文件
pytest tests/unit/test_security.py -v

# 运行单个测试函数
pytest tests/unit/test_security.py::TestSecurityPolicy::test_safe_code -v

# 调试模式
pytest tests/unit/test_security.py -v -s --pdb
```

## 最佳实践

1. **测试隔离**: 每个测试应该是独立的，不依赖其他测试的结果
2. **清理资源**: 使用夹具确保测试后清理临时文件和资源
3. **明确标记**: 为测试添加适当的标记，便于分类运行
4. **文档化**: 为测试函数添加清晰的文档字符串
5. **数据驱动**: 使用参数化测试来测试多种情况

## 故障排除

### 常见问题

1. **虚拟环境问题**
   ```bash
   # 重新创建虚拟环境
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **导入错误**
   ```bash
   # 确保PYTHONPATH设置正确
   export PYTHONPATH="${PWD}:${PYTHONPATH}"
   ```

3. **Docker相关测试失败**
   ```bash
   # 检查Docker服务
   docker ps
   
   # 启动服务
   ./start.sh dev
   ```

4. **权限问题**
   ```bash
   # 设置执行权限
   chmod +x test.sh run_tests.py
   ```

## 贡献指南

添加新测试时：

1. 选择合适的测试类型目录
2. 添加适当的pytest标记
3. 使用清晰的测试函数名
4. 添加文档字符串说明测试目的
5. 确保测试是独立和可重复的
