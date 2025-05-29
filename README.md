# SimplePySandbox - Python代码沙盒

一个基于FastAPI的安全Python代码执行沙盒，支持网络和文件操作。

## 📋 目录

- [项目概述](#项目概述)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [🚀 部署与使用](#-部署与使用)
  - [系统要求](#系统要求)
  - [快速部署](#快速部署)
  - [配置说明](#配置说明)
  - [生产环境部署](#生产环境部署)
  - [环境管理使用指南](#环境管理使用指南)
  - [完整使用示例](#完整使用示例)
  - [故障排除](#故障排除)
  - [性能优化](#性能优化)
- [📚 API详细文档](#-api详细文档)
- [执行代码](#执行代码)
- [健康检查](#健康检查)
- [项目结构](#项目结构)
- [安全特性](#安全特性)
- [🛠️ 环境管理](#️-环境管理)
- [开发指南](#开发指南)
- [许可证](#许可证)
- [贡献指南](#贡献指南)
- [支持](#支持)

## 项目概述

SimplePySandbox是一个轻量级的Python代码执行沙盒，通过REST API提供服务。它允许用户提交Python代码进行安全执行，并返回执行结果、输出以及生成的文件。

## 功能特性

- ✅ **安全的代码执行环境** - 使用Docker容器隔离执行环境
- ✅ **网络访问支持** - 允许代码进行网络请求
- ✅ **文件操作支持** - 支持文件读写操作
- ✅ **超时控制** - 可设置代码执行超时时间
- ✅ **完整的输出捕获** - 返回stdout、stderr和执行结果
- ✅ **文件结果返回** - 以base64编码返回生成的文件
- ✅ **RESTful API** - 基于FastAPI的现代Web API

## 快速开始

### 环境要求

- Python 3.10+
- Docker
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 构建Docker镜像

```bash
docker build -t python-sandbox .
```

## 📚 API详细文档

SimplePySandbox 提供了完整的RESTful API，支持代码执行、环境管理等功能。

### 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v1
- **内容类型**: `application/json`
- **字符编码**: UTF-8

### 代码执行API

#### 1. 基础代码执行

**POST** `/execute`

在默认环境中执行Python代码。

**请求示例**:
```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "timeout": 30
  }'
```

**完整参数说明**:
```json
{
  "code": "string",           // 必需：要执行的Python代码
  "timeout": 30,              // 可选：超时时间(秒)，默认30，最大300
  "files": {                  // 可选：输入文件(base64编码)
    "input.txt": "SGVsbG8="
  },
  "environment": "env-name"   // 可选：指定执行环境
}
```

**响应格式**:
```json
{
  "success": true,                    // 执行是否成功
  "stdout": "Hello, World!\n",       // 标准输出
  "stderr": "",                      // 标准错误
  "execution_time": 0.123,           // 执行时间(秒)
  "files": {                         // 生成的文件(base64编码)
    "output.txt": "VGVzdCBkYXRh"
  },
  "error": null                      // 错误信息
}
```

**错误响应**:
```json
{
  "success": false,
  "stdout": "",
  "stderr": "SyntaxError: invalid syntax",
  "execution_time": 0.001,
  "files": {},
  "error": "代码执行失败"
}
```

#### 2. 在指定环境中执行

**POST** `/execute-with-environment`

在指定的自定义环境中执行代码。

**请求示例**:
```bash
curl -X POST "http://localhost:8000/execute-with-environment" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import pandas as pd\nprint(pd.__version__)",
    "environment": "data-science",
    "timeout": 60
  }'
```

### 环境管理API

#### 1. 创建环境

**POST** `/environments`

创建新的执行环境。

**请求示例**:
```bash
curl -X POST "http://localhost:8000/environments" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ml-env",
    "description": "机器学习环境",
    "base_image": "python:3.11-slim",
    "setup_script": "pip install scikit-learn pandas numpy",
    "python_version": "3.11"
  }'
```

**参数说明**:
```json
{
  "name": "string",              // 必需：环境名称(字母数字和连字符)
  "description": "string",       // 必需：环境描述
  "base_image": "string",        // 必需：Docker基础镜像
  "setup_script": "string",      // 必需：安装脚本(bash)
  "python_version": "string"     // 必需：Python版本
}
```

**响应**:
```json
{
  "name": "ml-env",
  "description": "机器学习环境",
  "base_image": "python:3.11-slim",
  "docker_image": "sandbox-ml-env:latest",
  "status": "building",          // building/ready/failed
  "created_at": "2025-05-29T12:00:00Z",
  "last_used": null,
  "setup_script": "pip install...",
  "python_version": "3.11"
}
```

#### 2. 列出所有环境

**GET** `/environments`

获取所有环境的列表。

**请求示例**:
```bash
curl -X GET "http://localhost:8000/environments"
```

**响应**:
```json
{
  "environments": [
    {
      "name": "ml-env",
      "description": "机器学习环境",
      "status": "ready",
      "created_at": "2025-05-29T12:00:00Z",
      "last_used": "2025-05-29T12:30:00Z"
    }
  ],
  "total": 1
}
```

#### 3. 获取环境详情

**GET** `/environments/{environment_name}`

获取指定环境的详细信息。

**请求示例**:
```bash
curl -X GET "http://localhost:8000/environments/ml-env"
```

#### 4. 删除环境

**DELETE** `/environments/{environment_name}`

删除指定的环境和相关的Docker镜像。

**请求示例**:
```bash
curl -X DELETE "http://localhost:8000/environments/ml-env"
```

**响应**:
```json
{
  "message": "环境 'ml-env' 已删除"
}
```

### 系统API

#### 健康检查

**GET** `/health`

检查系统健康状态。

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-05-29T12:00:00Z"
}
```

#### API文档

**GET** `/docs`

访问交互式API文档(Swagger UI)。

**GET** `/redoc`

访问API文档(ReDoc格式)。

### 状态码说明

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 请求格式正确但语义错误 |
| 500 | Internal Server Error | 服务器内部错误 |

### 限制和约束

| 项目 | 限制 | 说明 |
|------|------|------|
| 代码长度 | 50KB | 单次提交的代码最大长度 |
| 执行时间 | 300秒 | 最大执行超时时间 |
| 文件大小 | 10MB | 单个文件最大大小 |
| 内存使用 | 512MB | 默认内存限制 |
| CPU使用 | 1.0核 | 默认CPU限制 |
| 并发执行 | 10个 | 同时执行的最大任务数 |

### 错误处理

#### 通用错误格式

```json
{
  "detail": "错误描述信息"
}
```

#### 常见错误

**1. 代码执行超时**
```json
{
  "success": false,
  "error": "代码执行超时(30秒)",
  "execution_time": 30.0
}
```

**2. 环境不存在**
```json
{
  "detail": "环境 'nonexistent-env' 不存在"
}
```

**3. 环境名称冲突**
```json
{
  "detail": "环境 'existing-env' 已存在"
}
```

**4. 文件过大**
```json
{
  "detail": "文件大小超过限制(10MB)"
}
```

### 客户端SDK示例

#### Python客户端

```python
import requests
import base64
import json

class SimplePySandboxClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def execute_code(self, code, timeout=30, files=None, environment=None):
        """执行代码"""
        payload = {
            "code": code,
            "timeout": timeout
        }
        
        if files:
            payload["files"] = files
        if environment:
            payload["environment"] = environment
            
        response = self.session.post(
            f"{self.base_url}/execute",
            json=payload
        )
        return response.json()
    
    def create_environment(self, name, description, setup_script, 
                          base_image="python:3.11-slim", python_version="3.11"):
        """创建环境"""
        payload = {
            "name": name,
            "description": description,
            "base_image": base_image,
            "setup_script": setup_script,
            "python_version": python_version
        }
        
        response = self.session.post(
            f"{self.base_url}/environments",
            json=payload
        )
        return response.json()
    
    def list_environments(self):
        """列出环境"""
        response = self.session.get(f"{self.base_url}/environments")
        return response.json()
    
    def get_environment(self, name):
        """获取环境详情"""
        response = self.session.get(f"{self.base_url}/environments/{name}")
        return response.json()
    
    def delete_environment(self, name):
        """删除环境"""
        response = self.session.delete(f"{self.base_url}/environments/{name}")
        return response.json()
    
    def health_check(self):
        """健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()

# 使用示例
client = SimplePySandboxClient()

# 执行代码
result = client.execute_code("print('Hello, World!')")
print(result)

# 创建环境
env_result = client.create_environment(
    name="test-env",
    description="测试环境",
    setup_script="pip install requests"
)
print(env_result)
```

#### JavaScript客户端

```javascript
class SimplePySandboxClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }
    
    async executeCode(code, options = {}) {
        const payload = {
            code,
            timeout: options.timeout || 30,
            ...options
        };
        
        const response = await fetch(`${this.baseUrl}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    async createEnvironment(config) {
        const response = await fetch(`${this.baseUrl}/environments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        return await response.json();
    }
    
    async listEnvironments() {
        const response = await fetch(`${this.baseUrl}/environments`);
        return await response.json();
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
}

// 使用示例
const client = new SimplePySandboxClient();

client.executeCode("print('Hello, World!')")
    .then(result => console.log(result));
```

## API文档

### 执行代码

**POST** `/execute` - 执行Python代码

**基础示例**:
```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")", "timeout": 30}'
```

**完整API文档**: 请参阅下方的 [📚 API详细文档](#-api详细文档) 章节

### 健康检查

**GET** `/health` - 检查服务状态

```bash
curl http://localhost:8000/health
```

## 项目结构

```
SimplePySandbox/
├── main.py                      # FastAPI主应用
├── manage_environments.py       # 环境管理脚本
├── run_tests.py                # 测试运行器
├── sandbox/                    # 沙盒核心模块
│   ├── __init__.py
│   ├── executor.py             # 代码执行器
│   ├── environment_manager.py   # 环境管理器
│   ├── security.py             # 安全策略
│   └── utils.py                # 工具函数
├── models/                     # 数据模型
│   ├── __init__.py
│   ├── request.py              # 请求/响应模型
│   └── environment.py          # 环境模型
├── config/                     # 配置模块
│   ├── __init__.py
│   └── settings.py             # 应用设置
├── tests/                      # 测试套件
│   ├── __init__.py
│   ├── conftest.py             # pytest配置
│   ├── README.md               # 测试文档
│   ├── data/                   # 测试数据
│   │   └── pythonocc_example.py
│   ├── unit/                   # 单元测试
│   │   ├── test_security.py
│   │   └── test_utils.py
│   ├── integration/            # 集成测试
│   │   ├── test_main.py
│   │   ├── test_timeout.py
│   │   ├── test_api_timeout.py
│   │   └── test_environment.py
│   ├── system/                 # 系统测试
│   │   └── test_complete_system.py
│   ├── performance/            # 性能测试
│   │   └── test_performance.py
│   └── legacy/                 # 遗留测试
├── environments/               # 环境脚本
│   ├── basic-python.sh
│   ├── pythonocc-stable.sh
│   └── pythonocc_cylinder.sh
├── examples/                   # 使用示例
│   ├── advanced_example.py
│   └── client_example.py
├── data/                       # 数据目录
│   └── environments/           # 环境数据
├── Dockerfile                  # Docker镜像配置
├── docker-compose.yml          # Docker Compose配置
├── k8s-deployment.yaml         # Kubernetes部署配置
├── requirements.txt            # Python依赖
├── pytest.ini                 # pytest配置
├── start.sh                    # 启动脚本
├── test.sh                     # 测试脚本
├── test_pythonocc_curl.sh     # PythonOCC测试脚本
├── .env.example               # 环境变量示例
├── .dockerignore              # Docker忽略文件
├── .gitignore                 # Git忽略文件
├── LICENSE                    # 许可证
├── README.md                  # 项目文档
├── DOCUMENTATION.md           # 详细文档
├── TESTING.md                 # 测试指南
└── TEST_REFACTORING_REPORT.md # 测试重构报告
```

## 安全特性

### 容器隔离

- 每次代码执行都在独立的Docker容器中运行
- 容器资源限制（CPU、内存）
- 网络访问控制

### 代码限制

- 执行时间限制
- 内存使用限制
- 禁止访问敏感系统资源
- 文件系统访问限制在工作目录

### 输入验证

- 代码长度限制
- 超时时间范围验证
- 文件大小限制

## 配置说明

环境变量配置：

- `SANDBOX_TIMEOUT`: 默认超时时间（秒）
- `MAX_CODE_LENGTH`: 最大代码长度
- `MAX_FILE_SIZE`: 最大文件大小（字节）
- `DOCKER_IMAGE`: 执行环境Docker镜像名称
- `WORK_DIR`: 容器内工作目录

## 开发指南

### 本地开发

1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 构建Docker镜像：`docker build -t python-sandbox .`
4. 启动开发服务器：`uvicorn main:app --reload`

### 测试

```bash
# 运行单元测试
python -m pytest tests/

# 运行集成测试
python -m pytest tests/integration/
```

### API测试示例

```bash
# 简单代码执行
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "timeout": 10
  }'

# 带文件输入的代码执行
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "with open(\"input.txt\", \"r\") as f:\n    content = f.read()\n    print(content)\nwith open(\"output.txt\", \"w\") as f:\n    f.write(\"Processed: \" + content)",
    "timeout": 10,
    "files": {
      "input.txt": "SGVsbG8gV29ybGQ="
    }
  }'
```

## 🚀 部署与使用

### 系统要求

- **操作系统**: Linux、macOS 或 Windows (推荐使用Linux生产环境)
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **内存**: 最少2GB，推荐4GB+
- **存储**: 最少10GB可用空间
- **网络**: 需要访问Docker Hub拉取镜像

### 快速部署

#### 方法一：Docker Compose (推荐)

1. **克隆项目**
```bash
git clone <repository-url>
cd SimplePySandbox
```

2. **启动服务**
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f sandbox-api
```

3. **验证部署**
```bash
# 健康检查
curl http://localhost:8000/health

# 测试代码执行
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, SimplePySandbox!\")"}'
```

#### 方法二：手动Docker部署

1. **构建镜像**
```bash
docker build -t simplepysandbox-sandbox-api:latest .
```

2. **创建网络和卷**
```bash
# 创建网络
docker network create sandbox-network

# 创建执行目录
sudo mkdir -p /tmp/sandbox-exec
sudo chmod 755 /tmp/sandbox-exec
```

3. **运行容器**
```bash
docker run -d \
  --name sandbox-api \
  --user "0:0" \
  -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/sandbox-exec:/app/data/temp \
  --network sandbox-network \
  simplepysandbox-sandbox-api:latest
```

### 配置说明

#### 环境变量配置

在`docker-compose.yml`或运行时设置以下环境变量：

```yaml
environment:
  # 基本配置
  - SANDBOX_TIMEOUT=30           # 默认超时时间(秒)
  - MAX_CODE_LENGTH=50000        # 最大代码长度
  - MAX_FILE_SIZE=10485760      # 最大文件大小(10MB)
  
  # Docker配置
  - DOCKER_IMAGE=python:3.11-slim  # 默认执行镜像
  - MEMORY_LIMIT=512m               # 内存限制
  - CPU_LIMIT=1.0                   # CPU限制
  - NETWORK_MODE=bridge             # 网络模式
  
  # 路径配置
  - WORK_DIR=/sandbox               # 容器工作目录
  - TEMP_DIR=/app/data/temp         # 临时文件目录
```

#### 高级配置

**1. 网络隔离配置**
```yaml
# 无网络访问模式
environment:
  - NETWORK_MODE=none

# 自定义网络模式
environment:
  - NETWORK_MODE=custom-network
```

**2. 资源限制调整**
```yaml
environment:
  - MEMORY_LIMIT=1g     # 1GB内存
  - CPU_LIMIT=2.0       # 2个CPU核心
```

**3. 安全强化**
```yaml
environment:
  - SECURITY_LEVEL=strict    # 严格安全模式
  - ALLOWED_MODULES=os,sys,json  # 允许的模块列表
```

### 生产环境部署

#### 1. 使用反向代理

**Nginx配置示例**
```nginx
upstream sandbox_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # API路由
    location / {
        proxy_pass http://sandbox_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 文件上传大小限制
    client_max_body_size 50M;
}
```

#### 2. SSL/HTTPS配置

```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

#### 3. 监控和日志

**Docker Compose监控配置**
```yaml
services:
  sandbox-api:
    # ... 其他配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # 健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 环境管理使用指南

#### 1. 创建自定义环境

**使用CLI工具**
```bash
# 创建数据科学环境
python manage_environments.py create data-science environments/data-science-pip.sh --wait

# 创建机器学习环境
python manage_environments.py create ml-env environments/machine-learning.sh --wait
```

**使用API直接创建**
```bash
curl -X POST http://localhost:8000/environments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-dev",
    "description": "Web开发环境",
    "base_image": "python:3.11-slim",
    "setup_script": "pip install fastapi uvicorn requests pandas",
    "python_version": "3.11"
  }'
```

#### 2. 环境脚本编写

**基础脚本模板**
```bash
#!/bin/bash
set -e  # 遇到错误时停止

echo "🔧 开始安装依赖..."

# 更新包管理器
apt-get update

# 安装系统依赖
apt-get install -y git curl

# 安装Python包
pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    requests

# 清理缓存
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "✅ 环境配置完成"
```

#### 3. 使用自定义环境

```python
import requests

# 在特定环境中执行代码
response = requests.post("http://localhost:8000/execute", json={
    "code": """
import pandas as pd
import numpy as np

# 创建数据
data = pd.DataFrame({
    'A': np.random.randn(10),
    'B': np.random.randn(10)
})

print("数据统计:")
print(data.describe())

# 保存到文件
data.to_csv('output.csv', index=False)
print("数据已保存到 output.csv")
""",
    "environment": "data-science",
    "timeout": 30
})

print(response.json())
```

### 完整使用示例

#### 1. 基础代码执行
```python
import requests
import base64

# 基础代码执行
def basic_execution():
    code = """
print("Hello, SimplePySandbox!")
import sys
print(f"Python version: {sys.version}")

# 创建文件
with open("hello.txt", "w") as f:
    f.write("Hello from sandbox!")
"""
    
    response = requests.post("http://localhost:8000/execute", json={
        "code": code,
        "timeout": 10
    })
    
    result = response.json()
    print("执行结果:", result["stdout"])
    
    # 下载生成的文件
    if "hello.txt" in result["files"]:
        file_content = base64.b64decode(result["files"]["hello.txt"])
        print("文件内容:", file_content.decode())

basic_execution()
```

#### 2. 文件处理示例
```python
def file_processing_example():
    # 准备输入文件
    input_data = "Name,Age,City\nAlice,25,New York\nBob,30,London"
    input_b64 = base64.b64encode(input_data.encode()).decode()
    
    code = """
import csv
import json

# 读取CSV文件
with open("input.csv", "r") as f:
    reader = csv.DictReader(f)
    data = list(reader)

print(f"读取了 {len(data)} 条记录")

# 转换为JSON
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)

print("数据已转换为JSON格式")
"""
    
    response = requests.post("http://localhost:8000/execute", json={
        "code": code,
        "files": {"input.csv": input_b64},
        "timeout": 15
    })
    
    result = response.json()
    if result["success"] and "output.json" in result["files"]:
        json_content = base64.b64decode(result["files"]["output.json"])
        print("JSON输出:", json_content.decode())

file_processing_example()
```

#### 3. 网络请求示例
```python
def network_request_example():
    code = """
import requests
import json

try:
    # 获取公共API数据
    response = requests.get("https://httpbin.org/json", timeout=10)
    data = response.json()
    
    print("API响应:")
    print(json.dumps(data, indent=2))
    
    # 保存响应
    with open("api_response.json", "w") as f:
        json.dump(data, f, indent=2)
        
except Exception as e:
    print(f"请求失败: {e}")
"""
    
    response = requests.post("http://localhost:8000/execute", json={
        "code": code,
        "timeout": 20
    })
    
    result = response.json()
    print("网络请求结果:", result["stdout"])

network_request_example()
```

### 故障排除

#### 常见问题

**1. Docker权限问题**
```bash
# 确保Docker socket权限正确
sudo chmod 666 /var/run/docker.sock

# 或者将用户加入docker组
sudo usermod -aG docker $USER
```

**2. 端口占用**
```bash
# 检查端口使用
sudo netstat -tlnp | grep :8000

# 修改端口
docker-compose down
# 编辑docker-compose.yml中的端口映射
docker-compose up -d
```

**3. 内存不足**
```bash
# 清理Docker资源
docker system prune -a

# 调整内存限制
docker-compose down
# 修改MEMORY_LIMIT环境变量
docker-compose up -d
```

**4. 环境构建失败**
```bash
# 查看构建日志
docker-compose logs sandbox-api

# 手动测试环境脚本
docker run --rm python:3.11-slim bash -c "你的脚本内容"
```

#### 调试模式

启用详细日志：
```yaml
environment:
  - LOG_LEVEL=DEBUG
  - PYTHONUNBUFFERED=1
```

### 性能优化

#### 1. 缓存优化
```bash
# 预拉取常用镜像
docker pull python:3.11-slim
docker pull python:3.9-slim
```

#### 2. 资源调优
```yaml
# 根据负载调整资源限制
environment:
  - MEMORY_LIMIT=1g      # 增加内存
  - CPU_LIMIT=2.0        # 增加CPU
  - CONCURRENT_LIMIT=10  # 并发执行限制
```

#### 3. 监控配置
```bash
# 使用cAdvisor监控容器
docker run -d \
  --name=cadvisor \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  gcr.io/cadvisor/cadvisor:latest
```

## 🛠️ 环境管理

SimplePySandbox 支持创建和管理自定义执行环境，您可以通过shell脚本配置容器依赖。

### 环境功能特性

- **多包管理器支持**: pip、conda、apt等
- **自定义基础镜像**: 支持Python、Miniconda等不同基础镜像
- **环境隔离**: 每个环境独立运行，互不影响
- **脚本安全检查**: 自动检测危险命令
- **持久化存储**: 环境配置和状态持久保存

### 创建环境

```bash
curl -X POST "http://localhost:8000/environments" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "data-science-env",
    "description": "数据科学环境",
    "base_image": "python:3.11-slim",
    "setup_script": "#!/bin/bash\nset -e\npip install numpy pandas matplotlib",
    "python_version": "3.11"
  }'
```

### 使用环境执行代码

```bash
curl -X POST "http://localhost:8000/execute-with-environment" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import pandas as pd\nprint(pd.__version__)",
    "environment": "data-science-env",
    "timeout": 30
  }'
```

### 环境脚本示例

项目提供了多个预定义的环境脚本示例：

- **data-science-pip.sh**: 基于pip的数据科学环境
- **data-science-conda.sh**: 基于conda的数据科学环境
- **machine-learning.sh**: 机器学习环境（包含深度学习框架）
- **web-development.sh**: Web开发环境（FastAPI、Django等）
- **basic-python.sh**: 基础Python工具环境

### 环境管理API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/environments` | GET | 列出所有环境 |
| `/environments` | POST | 创建新环境 |
| `/environments/{name}` | GET | 获取环境详情 |
| `/environments/{name}` | DELETE | 删除环境 |
| `/execute-with-environment` | POST | 在指定环境中执行代码 |

### 示例代码

```python
# 查看 examples/ 目录下的示例：
# - environment_example.py: 基础环境管理示例
# - conda_environment_example.py: Conda环境示例
# - web_api_environment_example.py: Web开发环境示例
```

## 许可证

MIT License

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 支持

如有问题或建议，请创建Issue或联系开发团队。
