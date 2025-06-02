![Cover](./cover.png)


# SimplePySandbox - 安全的Python代码执行沙盒

🐍 一个基于FastAPI的现代化Python代码执行沙盒，支持Docker容器化部署和自定义环境管理。

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 目录

- [项目特性](#-项目特性)
- [快速开始](#-快速开始)
- [部署方式](#-部署方式)
- [API示例](#-api示例)
- [API文档](#-api文档)
- [CLI工具](#-cli工具)
- [演示客户端](#-演示客户端)
- [项目结构](#-项目结构)
- [安全特性](#-安全特性)
- [性能指标](#-性能指标)
- [故障排除](#-故障排除)

## 🚀 项目特性

### 核心功能
- 🐳 **Docker容器化** - 完全隔离的安全执行环境
- 🌐 **RESTful API** - 基于FastAPI的现代Web API
- 📁 **文件操作** - 支持文件读写，Base64编码返回
- ⏱️ **超时控制** - 灵活的代码执行时间限制
- 🔒 **安全隔离** - 容器级别的安全边界
- 📊 **性能监控** - 执行时间和资源使用统计

### 环境管理
- 🎛️ **自定义环境** - 创建和管理专用执行环境
- 🐍 **多Python版本** - 支持不同Python版本
- 📦 **包管理** - 灵活的依赖安装和管理

### 开发者友好
- 📖 **完整文档** - Swagger UI自动生成API文档
- 🛠️ **CLI工具** - 命令行环境管理工具
- 💡 **示例客户端** - 功能完整的Python客户端

## ⚡ 快速开始

### 环境要求

- **Python 3.10+**
- **Docker** (推荐)
- **Conda/Miniconda** (可选)

### 1. 克隆项目

```bash
git clone <repository-url>
cd SimplePySandbox
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式 
# 使用docker启动，否则无法安全隔离
docker run -d -p 8000:8000 --name simplepysandbox simplepysandbox:latest
```

### 4. 验证服务

```bash
curl http://localhost:8000/health
```

## 🐳 部署方式

### Docker部署（推荐）

#### 1. 构建镜像

```bash
docker build -t simplepysandbox:latest .
```

#### 2. 运行容器

```bash
# 基础运行
docker run -d -p 8000:8000 --name simplepysandbox simplepysandbox:latest

# 带资源限制
docker run -d \
  -p 8000:8000 \
  --name simplepysandbox \
  --memory=1g \
  --cpus=1.0 \
  simplepysandbox:latest
```

#### 3. Docker Compose部署

```bash
docker-compose up -d
```

### 本地开发部署

#### 裸服务启动，便于开发和调试

```bash
# 启动服务
uvicorn main:app --reload
```

## 🔥 API示例

### 基础代码执行

#### 简单计算

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, SimplePySandbox!\")\nresult = 2 + 3\nprint(f\"2 + 3 = {result}\")",
    "timeout": 10
  }'
```

#### 数据处理示例

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import json\nimport csv\nfrom datetime import datetime\n\n# 创建数据\ndata = {\n  \"timestamp\": str(datetime.now()),\n  \"numbers\": [1, 2, 3, 4, 5],\n  \"sum\": sum([1, 2, 3, 4, 5])\n}\n\n# 保存为JSON\nwith open(\"result.json\", \"w\") as f:\n    json.dump(data, f, indent=2)\n\nprint(\"数据处理完成\")\nprint(f\"结果: {data}\")",
    "timeout": 15
  }'
```

### 环境操作示例

#### 1. 创建环境

```bash
curl -X POST "http://localhost:8000/environments" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "data-science",
    "description": "数据科学环境",
    "setup_script": "pip install numpy pandas matplotlib seaborn scikit-learn",
    "python_version": "3.11"
  }'
```

#### 2. 列出环境

```bash
curl -X GET "http://localhost:8000/environments"
```

#### 3. 在指定环境中执行代码

```bash
curl -X POST "http://localhost:8000/execute-with-environment" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import numpy as np\nimport pandas as pd\n\n# 创建数据\ndata = np.random.rand(10, 3)\ndf = pd.DataFrame(data, columns=[\"A\", \"B\", \"C\"])\n\nprint(\"数据概览:\")\nprint(df.describe())\n\n# 保存结果\ndf.to_csv(\"analysis.csv\", index=False)\nprint(\"\\n数据已保存到 analysis.csv\")",
    "environment": "data-science",
    "timeout": 30
  }'
```

#### 4. 删除环境

```bash
curl -X DELETE "http://localhost:8000/environments/data-science"
```

### Python客户端示例

```python
import requests
import json

class SimplePySandboxClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def execute_code(self, code, timeout=10, environment=None):
        payload = {"code": code, "timeout": timeout}
        if environment:
            payload["environment"] = environment
        
        response = requests.post(f"{self.base_url}/execute", json=payload)
        return response.json()
    
    def create_environment(self, name, setup_script, description="", python_version="3.11"):
        payload = {
            "name": name,
            "description": description,
            "setup_script": setup_script,
            "python_version": python_version
        }
        response = requests.post(f"{self.base_url}/environments", json=payload)
        return response.json()

# 使用示例
client = SimplePySandboxClient()

# 执行代码
result = client.execute_code("""
import math
numbers = [1, 4, 9, 16, 25]
sqrt_numbers = [math.sqrt(x) for x in numbers]
print(f"原数字: {numbers}")
print(f"平方根: {sqrt_numbers}")
""")

print(f"执行结果: {result}")
```

## 📚 API文档

### 接口概览

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | API信息 |
| GET | `/health` | 健康检查 |
| POST | `/execute` | 执行代码 |
| POST | `/execute-with-environment` | 在指定环境中执行代码 |
| GET | `/environments` | 列出所有环境 |
| POST | `/environments` | 创建环境 |
| GET | `/environments/{name}` | 获取环境详情 |
| DELETE | `/environments/{name}` | 删除环境 |

### 请求/响应格式

#### 执行代码 (POST /execute)

**请求**:
```json
{
  "code": "string",           // 必需：Python代码
  "timeout": 10,             // 可选：超时时间(秒)
  "files": {                 // 可选：输入文件
    "filename": "base64content"
  }
}
```

**响应**:
```json
{
  "success": true,           // 执行状态
  "stdout": "output text",   // 标准输出
  "stderr": "",              // 错误输出
  "error": null,             // 错误信息
  "execution_time": 0.123,   // 执行时间(秒)
  "files": {                 // 生成的文件
    "result.txt": "base64content"
  }
}
```

#### 创建环境 (POST /environments)

**请求**:
```json
{
  "name": "env-name",        // 必需：环境名称
  "description": "描述",      // 可选：环境描述
  "setup_script": "pip install pandas", // 必需：设置脚本
  "python_version": "3.11"   // 可选：Python版本
}
```

**响应**:
```json
{
  "name": "env-name",
  "description": "描述",
  "status": "building",
  "python_version": "3.11",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### 交互式文档

启动服务后，访问以下地址查看完整的API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🛠️ CLI工具

SimplePySandbox提供了强大的命令行工具 `manage_environments.py` 用于环境管理。

### 安装与使用

```bash
# 确保项目依赖已安装
pip install -r requirements.txt

# 查看帮助
python manage_environments.py --help
```

### 基础命令(需要确保服务正在运行，如果修改了服务url请使用url参数传递)

#### 1. 列出环境

```bash
python manage_environments.py list
```

输出示例：
```
📋 环境列表:
   共 2 个环境:

   ✅ data-science
      状态: ready
      描述: 数据科学环境
      Python版本: 3.11
      创建时间: 2025-01-01T10:00:00Z

   🔧 ml-env
      状态: building
      描述: 机器学习环境
      Python版本: 3.10
      创建时间: 2025-01-01T11:00:00Z
```

#### 2. 创建环境

```bash
# 基础创建
python manage_environments.py create my-env ./environments/setup.sh

# 带参数创建
python manage_environments.py create ml-env ./environments/ml.sh \
  --description "机器学习环境" \
  --python-version 3.10

# 创建并等待完成
python manage_environments.py create data-env ./environments/data.sh \
  --wait \
  --wait-timeout 15
```

##### 2.1 参数说明：
```bash
python manage_environments.py create <name> <setup_script> [--description "描述"] [--python-version 3.11] [--wait] [--wait-timeout 10] [--url <服务地址>]
```
其中`setup_script`是环境配置脚本的路径，用于在环境创建后安装依赖以及一些自定义动作的执行。


#### 3. 查看环境详情

```bash
python manage_environments.py info my-env
```

输出示例：
```
🔍 环境详情: my-env
   ✅ 名称: my-env
   📝 描述: 自定义环境
   🐍 Python版本: 3.11
   📊 状态: ready
   📅 创建时间: 2025-01-01T10:00:00Z
   🕐 最后使用: 2025-01-01T12:00:00Z
```

#### 4. 删除环境

```bash
python manage_environments.py delete my-env
```

#### 5. 等待环境构建完成

```bash
# 等待默认10分钟
python manage_environments.py wait my-env

# 自定义等待时间
python manage_environments.py wait my-env --timeout 20
```

### 环境配置脚本示例

创建环境配置脚本 `environments/data-science.sh`：

```bash
#!/bin/bash
# 数据科学环境配置脚本

set -e

echo "🔧 配置数据科学环境..."

# 安装数据科学库
pip install numpy pandas matplotlib seaborn scikit-learn jupyter

# 安装额外工具
pip install requests beautifulsoup4 plotly

echo "✅ 数据科学环境配置完成"
```

使用脚本创建环境：

```bash
python manage_environments.py create data-science ./environments/data-science.sh \
  --description "完整的数据科学环境" \
  --python-version 3.11 \
  --wait
```

### 高级功能

#### 指定API地址

```bash
python manage_environments.py --url http://remote-server:8000 list
```

#### 批量操作

```bash
# 批量创建环境
for env in data-science ml-ops web-scraping; do
  python manage_environments.py create $env ./environments/${env}.sh --wait
done
```

## 💡 演示客户端

项目包含一个功能完整的演示客户端 `demo_client.py`，展示了所有主要功能。

### 运行演示

```bash
# 确保服务正在运行
uvicorn main:app --host 0.0.0.0 --port 8000

# 运行演示客户端
python example/demo_client.py
```

### 演示内容

演示客户端包含以下功能展示：

#### 1. 基础代码执行
```python
def demo_basic_usage():
    """演示基本用法"""
    client = SimplePySandboxClient()
    
    # 健康检查
    health = client.health_check()
    print(f"服务状态: {health['status']}")
    
    # 基本代码执行
    basic_code = """
print("Hello from SimplePySandbox!")
import sys
print(f"Python版本: {sys.version}")

numbers = [1, 2, 3, 4, 5]
result = sum(x**2 for x in numbers)
print(f"平方和: {result}")
"""
    
    result = client.execute_code(basic_code)
    client.print_result(result)
```

#### 2. 文件操作演示
```python
def demo_file_operations():
    """演示文件操作"""
    file_code = """
import json
import csv
from datetime import datetime

# 创建JSON文件
data = {
    "timestamp": str(datetime.now()),
    "message": "SimplePySandbox测试",
    "numbers": list(range(1, 11)),
    "status": "success"
}

with open("test_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# 创建CSV文件
csv_data = [
    ["姓名", "年龄", "城市"],
    ["张三", "25", "北京"],
    ["李四", "30", "上海"],
    ["王五", "28", "深圳"]
]

with open("test_data.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_data)

print("✅ 文件创建完成!")
"""
    
    result = client.execute_code(file_code)
    client.print_result(result)
```

#### 3. 性能测试
```python
def demo_performance_test():
    """演示性能测试"""
    perf_code = """
import time
import math

print("🔥 性能测试开始...")

# 数学计算测试
start = time.time()
result = sum(math.sqrt(i) for i in range(10000))
math_time = time.time() - start
print(f"数学计算: {result:.2f}, 耗时: {math_time:.3f}秒")

# 字符串操作测试
start = time.time()
text = "SimplePySandbox " * 1000
operations = [
    text.upper(),
    text.lower(),
    text.replace("Sandbox", "环境"),
    "".join(reversed(text))
]
string_time = time.time() - start
print(f"字符串操作: {len(operations)}个操作, 耗时: {string_time:.3f}秒")

print("✅ 性能测试完成!")
"""
    
    result = client.execute_code(perf_code, timeout=20)
    client.print_result(result)
```

#### 4. 错误处理演示
```python
def demo_error_handling():
    """演示错误处理"""
    # 语法错误测试
    syntax_error_code = """
print("语法错误测试")
if True  # 缺少冒号
    print("这会导致语法错误")
"""
    
    result = client.execute_code(syntax_error_code)
    client.print_result(result)
    
    # 运行时错误测试
    runtime_error_code = """
print("运行时错误测试")
x = 10
y = 0
result = x / y  # 除零错误
"""
    
    result = client.execute_code(runtime_error_code)
    client.print_result(result)
```

#### 5. 环境管理演示
```python
def demo_environment_management():
    """演示环境管理"""
    client = SimplePySandboxClient()
    
    # 列出环境
    envs = client.list_environments()
    print(f"发现 {envs['total']} 个环境")
    
    # 创建测试环境
    setup_script = """
pip install requests beautifulsoup4
echo "环境设置完成"
"""
    
    try:
        result = client.create_environment(
            name="demo-env",
            description="演示环境",
            setup_script=setup_script
        )
        print("✅ 环境创建成功")
    except Exception as e:
        print(f"环境创建失败: {e}")
```

### 自定义演示

您可以基于演示客户端创建自己的测试用例：

```python
from demo_client import SimplePySandboxClient

def my_custom_demo():
    client = SimplePySandboxClient()
    
    # 您的自定义代码
    custom_code = """
# 在这里编写您的测试代码
import requests
import json

# 示例：获取天气数据
response = requests.get("https://api.openweathermap.org/data/2.5/weather?q=Beijing&appid=your_api_key")
print("API请求完成")
"""
    
    result = client.execute_code(custom_code, timeout=30)
    client.print_result(result)

if __name__ == "__main__":
    my_custom_demo()
```

## 📁 项目结构

```
SimplePySandbox/
├── main.py                    # FastAPI应用主文件
├── requirements.txt           # Python依赖
├── Dockerfile                 # Docker镜像构建文件
├── docker-compose.yml         # Docker Compose配置
├── manage_environments.py     # CLI环境管理工具
├── config/                   # 配置文件
│   ├── __init__.py
│   └── settings.py           # 应用设置
├── models/                   # 数据模型
│   ├── __init__.py
│   ├── request.py           # 请求模型
│   └── environment.py       # 环境模型
├── sandbox/                  # 沙盒核心模块
│   ├── __init__.py
│   ├── executor.py          # 代码执行器
│   ├── environment_manager.py # 环境管理器
│   ├── security.py          # 安全模块
│   └── utils.py             # 工具函数
├── environments/             # 环境配置脚本
│   └── pythonocc-stable.sh  # 示例环境脚本
├── data/                     # 数据目录
│   ├── environments.json    # 环境配置数据
│   └── conda_envs/          # Conda环境数据
├── 
├── examples/                 # 示例代码
    ├── demo_client.py    # 客户端示例
    └── advanced_example.py  # 高级用法示例
```

## 🔒 安全特性

### 容器级隔离
- **Docker容器** - 完全隔离的执行环境
- **资源限制** - CPU和内存使用限制
- **网络隔离** - 可选的网络访问控制
- **文件系统隔离** - 沙盒目录限制

### 代码执行安全
- **超时控制** - 防止无限循环和长时间运行
- **权限限制** - 非root用户执行
- **包管理** - 受控的依赖安装
- **错误隔离** - 异常不会影响主服务

### API安全
- **输入验证** - 严格的请求参数验证
- **错误处理** - 安全的错误信息返回
- **资源限制** - 请求大小和频率限制
- **日志记录** - 全面的操作日志

## 📊 性能指标

### 基准测试结果

| 操作类型 | 平均响应时间 | 内存使用 | CPU使用 |
|----------|-------------|----------|---------|
| 简单计算 | 15-30ms | ~100MB | <5% |
| 文件操作 | 20-40ms | ~120MB | <10% |
| 网络请求 | 100-300ms | ~150MB | <15% |
| 数据处理 | 50-200ms | ~200MB | <20% |

### 资源限制

| 资源类型 | 默认限制 | 最大限制 | 可配置 |
|----------|----------|----------|--------|
| 内存 | 512MB | 2GB | ✅ |
| CPU | 1.0核 | 2.0核 | ✅ |
| 执行时间 | 30秒 | 300秒 | ✅ |
| 文件大小 | 10MB | 100MB | ✅ |
| 代码长度 | 50KB | 500KB | ✅ |

### 性能优化建议

#### 生产环境配置
```bash
# Docker运行配置
docker run -d \
  -p 8000:8000 \
  --name simplepysandbox \
  --memory=1g \
  --cpus=2.0 \
  --restart=unless-stopped \
  simplepysandbox:latest
```

#### 环境变量调优
```bash
export MAX_EXECUTION_TIME=60
export MAX_CODE_LENGTH=100000
export MAX_FILE_SIZE=50000000
export LOG_LEVEL=INFO
```

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败

**问题**: `uvicorn: command not found`
```bash
# 解决方案
pip install uvicorn[standard]
```

**问题**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# 解决方案
pip install -r requirements.txt
```

#### 2. Docker相关问题

**问题**: `docker: Cannot connect to the Docker daemon`
```bash
# 解决方案
sudo systemctl start docker  # Linux
# 或启动Docker Desktop (macOS/Windows)
```

**问题**: `Permission denied while trying to connect to Docker daemon`
```bash
# 解决方案
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. 环境创建失败

**问题**: 环境状态一直是 `building`
```bash
# 检查环境状态
python manage_environments.py info env-name

# 查看Docker日志
docker logs simplepysandbox
```

**问题**: `Environment creation failed`
```bash
# 检查环境脚本
cat environments/script.sh

# 验证脚本权限
chmod +x environments/script.sh
```

#### 4. 代码执行超时

**问题**: 代码执行总是超时
```bash
# 增加超时时间
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"code": "import time; time.sleep(5)", "timeout": 30}'
```

#### 5. 网络连接问题

**问题**: API请求失败
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查端口占用
netstat -tlnp | grep :8000
```

### 调试模式

#### 启用详细日志
```bash
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

#### 查看容器日志
```bash
# 查看实时日志
docker logs -f simplepysandbox

# 查看最近日志
docker logs --tail 100 simplepysandbox
```

#### 性能监控
```bash
# 监控容器资源使用
docker stats simplepysandbox

# 监控系统资源
htop
```

### 获取支持

如果遇到问题：

1. **查看文档** - 完整的部署和使用文档
2. **检查日志** - 查看应用和容器日志
3. **运行测试** - 使用 `demo_client.py` 验证功能
4. **性能分析** - 查看 `TEST_REPORT.md` 了解性能基准

---

## 📄 许可证

本项目采用 MIT 许可证。详情请参见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🙏 致谢

感谢所有贡献者和开源社区的支持！

---

**SimplePySandbox** - 让Python代码执行更安全、更简单！ 🚀
