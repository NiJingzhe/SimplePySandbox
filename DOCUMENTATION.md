# SimplePySandbox 完整文档

## 🆕 最新更新日志

### v1.0.1 (2025-05-29) - 最新稳定版
**主要修复和改进：**

✅ **测试系统完善**
- 修复单元测试中的2个失败案例
- 实现自动化测试脚本 `test.sh` 支持多种测试模式
- 所有20个单元测试和6个集成测试全部通过

🔧 **安全机制增强**
- 增强字符串模式检测，支持正则表达式匹配危险代码模式
- 修复文件扩展名处理边缘情况（文件名以点结尾的情况）
- 加强对 `eval`, `exec`, `__import__` 等危险函数的检测

🐳 **Docker执行引擎优化**
- 移除不支持的超时参数，解决Docker API兼容性问题
- 修复容器分离模式参数冲突
- 优化容器资源管理和清理机制

⚠️ **废弃警告修复**
- 修复所有Pydantic废弃警告，迁移到ConfigDict格式
- 替换过时的datetime.utcnow()为timezone-aware实现
- 确保代码与最新依赖版本兼容

🔄 **自动化改进**
- test.sh脚本自动激活虚拟环境
- 集成测试自动启动/停止服务
- 改进错误处理和日志输出

## 📖 项目概述

SimplePySandbox 是一个基于 FastAPI 的安全 Python 代码执行沙盒，提供 REST API 接口用于安全地执行 Python 代码。项目使用 Docker 容器技术实现代码隔离，支持网络访问和文件操作，适用于在线代码编辑器、教育平台、代码测试等场景。

### 核心特性

- 🔒 **安全的代码执行环境** - 基于Docker容器的隔离执行
- 🌐 **网络访问支持** - 允许代码进行HTTP请求
- 📁 **文件操作支持** - 支持文件读写和文件返回
- ⏰ **超时控制** - 可配置的代码执行超时机制
- 📊 **完整的输出捕获** - 返回stdout、stderr和执行时间
- 🔧 **RESTful API** - 现代化的Web API接口
- 🧪 **完整的测试覆盖** - 单元测试、集成测试、性能测试
- 🐳 **容器化部署** - Docker和Kubernetes支持

---

## 📁 项目结构详解

```
SimplePySandbox/
├── 📋 核心配置文件
│   ├── main.py                 # FastAPI主应用入口
│   ├── requirements.txt        # Python依赖包列表
│   ├── pytest.ini            # pytest测试配置
│   ├── .env.example           # 环境变量示例文件
│   ├── .gitignore             # Git忽略文件配置
│   └── .dockerignore          # Docker构建忽略文件
│
├── 🏗️ 容器化部署文件
│   ├── Dockerfile             # Docker镜像构建文件
│   ├── docker-compose.yml     # Docker Compose服务编排
│   └── k8s-deployment.yaml    # Kubernetes部署配置
│
├── 🔧 自动化脚本
│   ├── start.sh               # 项目启动脚本
│   └── test.sh                # 自动化测试脚本
│
├── 🧪 测试文件
│   ├── test_main.py           # API集成测试
│   ├── test_security.py       # 安全模块单元测试
│   └── test_utils.py          # 工具模块单元测试
│
├── 📚 文档文件
│   ├── README.md              # 项目介绍和快速开始
│   ├── TESTING.md             # 测试指南和说明
│   └── DOCUMENTATION.md       # 完整项目文档（本文件）
│
├── 🏛️ 应用模块
│   ├── config/                # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py        # 应用配置和环境变量
│   │
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   └── request.py         # API请求和响应模型
│   │
│   ├── sandbox/               # 沙盒核心模块
│   │   ├── __init__.py
│   │   ├── executor.py        # 代码执行引擎
│   │   ├── security.py        # 安全策略和检查
│   │   └── utils.py           # 工具函数和辅助方法
│   │
│   └── examples/              # 使用示例
│       ├── client_example.py  # 客户端调用示例
│       └── advanced_example.py # 高级功能示例
```

---

## 🔧 工具文件详细说明

### 📋 核心配置文件

#### `main.py` - FastAPI主应用
- **作用**: 应用程序的主入口点，定义API路由和中间件
- **功能**:
  - 配置CORS中间件支持跨域请求
  - 定义应用生命周期管理
  - 实现健康检查和代码执行API端点
  - 集成代码执行器和安全策略

#### `requirements.txt` - 依赖管理
- **作用**: 定义项目所需的Python包及版本
- **主要依赖**:
  - `fastapi`: Web框架
  - `uvicorn`: ASGI服务器
  - `docker`: Docker客户端
  - `pydantic`: 数据验证
  - `pytest`: 测试框架

#### `pytest.ini` - 测试配置
- **作用**: 配置pytest测试框架的行为
- **配置内容**:
  - 测试文件发现规则
  - 测试输出格式
  - 测试标记定义

### 🏗️ 容器化部署文件

#### `Dockerfile` - Docker镜像构建
- **作用**: 定义Docker镜像的构建过程
- **特性**:
  - 基于Python 3.11-slim镜像
  - 安装系统依赖和Python包
  - 创建非root用户提高安全性
  - 配置健康检查机制
  - 暴露8000端口

#### `docker-compose.yml` - 服务编排
- **作用**: 定义多容器应用的服务配置
- **配置**:
  - 服务端口映射
  - Docker socket挂载（用于容器内启动容器）
  - 环境变量配置
  - 健康检查和重启策略
  - 网络配置

#### `k8s-deployment.yaml` - Kubernetes部署
- **作用**: 定义Kubernetes集群中的部署配置
- **包含**: Deployment、Service、ConfigMap等资源定义

### 🔧 自动化脚本

#### `start.sh` - 项目启动脚本
- **作用**: 自动化项目启动流程
- **功能**:
  - 依赖检查（Python、Docker）
  - 虚拟环境管理
  - 依赖安装
  - Docker镜像构建
  - 多种启动模式（开发/生产/Docker）
  - 彩色日志输出

#### `test.sh` - 自动化测试脚本
- **作用**: 提供完整的测试解决方案
- **功能**:
  - 单元测试执行
  - 集成测试执行
  - 性能测试和压力测试
  - 代码质量检查
  - 安全检查
  - 测试报告生成
  - Docker测试支持

### 🧪 测试文件

#### `test_main.py` - API集成测试
- **作用**: 测试FastAPI应用的完整功能
- **测试内容**:
  - 根路径响应
  - 健康检查端点
  - 代码执行API
  - 文件处理功能
  - 错误处理机制

#### `test_security.py` - 安全模块测试
- **作用**: 验证安全策略的有效性
- **测试内容**:
  - 危险代码检测
  - 模块导入限制
  - 内置函数访问控制
  - 属性访问检查
  - 字符串模式匹配

#### `test_utils.py` - 工具模块测试
- **作用**: 测试工具函数的正确性
- **测试内容**:
  - 临时目录管理
  - 文件名验证
  - 输出清理
  - 文件扩展名处理
  - 文件大小格式化

### 🏛️ 应用模块

#### `config/settings.py` - 配置管理
- **作用**: 管理应用配置和环境变量
- **配置项**:
  - 沙盒执行超时时间
  - 代码长度限制
  - 文件大小限制
  - Docker镜像配置
  - 资源限制设置

#### `models/request.py` - 数据模型
- **作用**: 定义API请求和响应的数据结构
- **模型**:
  - `ExecuteRequest`: 代码执行请求模型
  - `ExecuteResponse`: 代码执行响应模型
  - `HealthResponse`: 健康检查响应模型

#### `sandbox/executor.py` - 代码执行引擎
- **作用**: 核心的代码执行逻辑
- **功能**:
  - Docker容器管理
  - 代码执行控制
  - 输出捕获
  - 文件处理
  - 资源限制
  - 安全检查集成

#### `sandbox/security.py` - 安全策略
- **作用**: 实现代码安全检查机制
- **功能**:
  - AST语法树分析
  - 危险函数检测
  - 模块导入限制
  - 属性访问控制
  - 安全的全局命名空间创建

#### `sandbox/utils.py` - 工具函数
- **作用**: 提供通用的辅助功能
- **功能**:
  - 临时目录创建和清理
  - 文件名安全验证
  - 输出内容清理
  - 文件类型判断
  - 文件大小格式化

---

## 🚀 部署方法

### 1. 本地开发部署

#### 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd SimplePySandbox

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 启动开发服务器
```bash
# 方法1: 使用启动脚本
chmod +x start.sh
./start.sh dev

# 方法2: 直接使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 验证部署
```bash
# 检查健康状态
curl http://localhost:8000/health

# 测试代码执行
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")"}'
```

### 2. Docker部署

#### 单容器部署
```bash
# 构建镜像
docker build -t python-sandbox .

# 运行容器
docker run -d \
  --name sandbox-api \
  -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e SANDBOX_TIMEOUT=30 \
  -e MAX_CODE_LENGTH=100000 \
  python-sandbox
```

#### Docker Compose部署
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 健康检查
```bash
# 检查容器状态
docker ps
docker-compose ps

# 检查服务健康
curl http://localhost:8000/health
```

### 3. Kubernetes部署

#### 部署到集群
```bash
# 应用配置
kubectl apply -f k8s-deployment.yaml

# 检查部署状态
kubectl get deployments
kubectl get pods
kubectl get services

# 查看日志
kubectl logs -f deployment/sandbox-api
```

#### 配置说明
- **Deployment**: 定义应用部署规格
- **Service**: 暴露服务端口
- **ConfigMap**: 管理配置文件
- **Ingress**: 配置外部访问（可选）

### 4. 生产环境部署

#### 环境变量配置
```bash
# 创建.env文件
cat > .env << EOF
SANDBOX_TIMEOUT=30
MAX_TIMEOUT=300
MAX_CODE_LENGTH=100000
MAX_FILE_SIZE=10485760
DOCKER_IMAGE=python:3.11-slim
MEMORY_LIMIT=512m
CPU_LIMIT=1
LOG_LEVEL=INFO
EOF
```

#### 性能优化
```bash
# 使用生产级ASGI服务器
pip install gunicorn

# 启动多worker进程
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### 监控和日志
```bash
# 配置日志轮转
# 使用Prometheus监控
# 配置健康检查
# 设置告警规则
```

---

## 📡 API使用方法

### API概览

SimplePySandbox提供简洁的REST API接口，主要包含两个端点：

- `GET /health` - 健康检查
- `POST /execute` - 执行Python代码

### 1. 健康检查API

#### 端点信息
- **URL**: `GET /health`
- **描述**: 检查服务运行状态
- **认证**: 无需认证

#### 请求示例
```bash
curl -X GET http://localhost:8000/health
```

#### 响应示例
```json
{
  "status": "healthy",
  "timestamp": "2025-05-29T10:30:00.123456Z"
}
```

#### 响应字段
- `status` (string): 服务状态，"healthy"表示正常
- `timestamp` (string): ISO格式的时间戳

### 2. 代码执行API

#### 端点信息
- **URL**: `POST /execute`
- **描述**: 执行Python代码并返回结果
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | string | 是 | - | 要执行的Python代码 |
| `timeout` | integer | 否 | 30 | 执行超时时间（秒），最大300 |
| `files` | object | 否 | {} | 输入文件，key为文件名，value为base64编码内容 |

#### 请求示例

##### 基础代码执行
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")\nprint(2 + 3)"
  }'
```

##### 带超时设置
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import time\ntime.sleep(2)\nprint(\"Done!\")",
    "timeout": 10
  }'
```

##### 带文件输入
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "with open(\"input.txt\", \"r\") as f:\n    content = f.read()\nprint(f\"File content: {content}\")",
    "files": {
      "input.txt": "SGVsbG8gZnJvbSBmaWxlIQ=="
    }
  }'
```

#### 响应格式

##### 成功响应
```json
{
  "success": true,
  "stdout": "Hello, World!\n5\n",
  "stderr": "",
  "execution_time": 0.045,
  "files": {},
  "error": null
}
```

##### 错误响应
```json
{
  "success": false,
  "stdout": "",
  "stderr": "Traceback (most recent call last):\n  File \"/tmp/code.py\", line 1, in <module>\n    print(undefined_variable)\nNameError: name 'undefined_variable' is not defined\n",
  "execution_time": 0.023,
  "files": {},
  "error": "Code execution failed"
}
```

##### 安全策略拒绝
```json
{
  "success": false,
  "stdout": "",
  "stderr": "",
  "execution_time": 0.001,
  "files": {},
  "error": "Security policy violation: Dangerous builtin function detected: eval"
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | boolean | 执行是否成功 |
| `stdout` | string | 标准输出内容 |
| `stderr` | string | 标准错误输出 |
| `execution_time` | float | 执行时间（秒） |
| `files` | object | 生成的文件，key为文件名，value为base64编码内容 |
| `error` | string\|null | 错误信息 |

### 3. 客户端SDK示例

#### Python客户端
```python
import requests
import base64
import json

class SandboxClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def execute_code(self, code, timeout=30, files=None):
        """执行Python代码"""
        payload = {
            "code": code,
            "timeout": timeout
        }
        
        if files:
            payload["files"] = {
                name: base64.b64encode(content.encode()).decode()
                for name, content in files.items()
            }
        
        response = requests.post(
            f"{self.base_url}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        return response.json()
    
    def health_check(self):
        """检查服务健康状态"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# 使用示例
client = SandboxClient()

# 检查健康状态
health = client.health_check()
print(f"Service status: {health['status']}")

# 执行简单代码
result = client.execute_code("print('Hello from sandbox!')")
print(f"Output: {result['stdout']}")

# 执行带文件的代码
files = {"data.txt": "Hello, World!"}
code = """
with open('data.txt', 'r') as f:
    content = f.read()
print(f"File content: {content}")

with open('output.txt', 'w') as f:
    f.write(content.upper())
"""
result = client.execute_code(code, files=files)
print(f"Generated files: {list(result['files'].keys())}")
```

#### JavaScript客户端
```javascript
class SandboxClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async executeCode(code, timeout = 30, files = {}) {
        const payload = {
            code,
            timeout,
            files: {}
        };
        
        // 转换文件为base64
        for (const [name, content] of Object.entries(files)) {
            payload.files[name] = btoa(content);
        }
        
        const response = await fetch(`${this.baseUrl}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
}

// 使用示例
const client = new SandboxClient();

// 检查健康状态
client.healthCheck().then(health => {
    console.log(`Service status: ${health.status}`);
});

// 执行代码
client.executeCode(`
import requests
response = requests.get('https://httpbin.org/json')
print(response.json())
`).then(result => {
    if (result.success) {
        console.log('Output:', result.stdout);
    } else {
        console.error('Error:', result.error);
    }
});
```

### 4. 高级使用场景

#### 数据科学分析
```python
code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# 创建示例数据
data = {
    'x': np.random.randn(100),
    'y': np.random.randn(100)
}
df = pd.DataFrame(data)

# 生成图表
plt.figure(figsize=(10, 6))
plt.scatter(df['x'], df['y'], alpha=0.6)
plt.title('Random Data Scatter Plot')
plt.xlabel('X values')
plt.ylabel('Y values')

# 保存图表
plt.savefig('plot.png', dpi=150, bbox_inches='tight')
plt.close()

# 统计分析
stats = df.describe()
print("统计摘要:")
print(stats)

# 保存CSV
df.to_csv('data.csv', index=False)
print("\\n数据已保存到 data.csv")
print("图表已保存到 plot.png")
"""

result = client.execute_code(code, timeout=60)
```

#### 网络爬虫
```python
code = """
import requests
from bs4 import BeautifulSoup
import json

# 爬取网页数据
url = 'https://httpbin.org/html'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 提取标题
title = soup.find('title').text if soup.find('title') else 'No title'
print(f"页面标题: {title}")

# 提取所有链接
links = []
for link in soup.find_all('a'):
    href = link.get('href')
    text = link.text.strip()
    if href:
        links.append({'url': href, 'text': text})

# 保存结果
result = {
    'title': title,
    'links': links,
    'total_links': len(links)
}

with open('scraping_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"找到 {len(links)} 个链接")
print("结果已保存到 scraping_result.json")
"""

result = client.execute_code(code, timeout=30)
```

#### 文件处理
```python
# 准备输入文件
files = {
    "input.csv": "name,age,city\nAlice,25,New York\nBob,30,London\nCharlie,35,Tokyo"
}

code = """
import pandas as pd
import json

# 读取CSV文件
df = pd.read_csv('input.csv')
print("原始数据:")
print(df)

# 数据处理
df['age_group'] = df['age'].apply(lambda x: 'Young' if x < 30 else 'Adult')
df_sorted = df.sort_values('age')

print("\\n处理后的数据:")
print(df_sorted)

# 保存处理结果
df_sorted.to_csv('processed.csv', index=False)

# 创建统计报告
stats = {
    'total_records': len(df),
    'average_age': df['age'].mean(),
    'cities': df['city'].unique().tolist(),
    'age_groups': df['age_group'].value_counts().to_dict()
}

with open('report.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("\\n统计报告:")
print(json.dumps(stats, indent=2))
"""

result = client.execute_code(code, files=files, timeout=30)
```

---

## 🕐 Timeout约束机制详解

SimplePySandbox实现了多层timeout约束机制，确保代码执行不会无限期运行，保护系统资源：

### 1. 配置层面的Timeout控制

#### 默认配置（config/settings.py）
```python
SANDBOX_TIMEOUT: int = 30      # 默认超时时间（秒）
MAX_TIMEOUT: int = 300         # 最大允许超时时间（秒）
```

#### 环境变量配置
```bash
# 在 .env 文件或环境变量中设置
SANDBOX_TIMEOUT=30
MAX_TIMEOUT=300
```

### 2. API层面的Timeout验证

#### 请求参数验证
- 如果未指定timeout，使用默认值30秒
- 如果指定的timeout超过MAX_TIMEOUT，API返回422错误
- 使用Pydantic模型进行参数验证

```python
# models/request.py
class ExecuteRequest(BaseModel):
    timeout: int = Field(
        default=30, 
        ge=1, 
        le=300,  # 自动验证不超过最大值
        description="执行超时时间（秒）"
    )
```

#### API错误响应示例
```json
{
  "detail": [{
    "type": "less_than_equal",
    "loc": ["body", "timeout"],
    "msg": "Input should be less than or equal to 300",
    "input": 500
  }]
}
```

### 3. Docker容器级别的Timeout实现

#### 实现机制
SimplePySandbox使用Docker API的`container.wait(timeout=seconds)`方法实现精确的超时控制：

```python
# sandbox/executor.py
def _run_container_sync(self, config: Dict, timeout: int) -> Dict:
    container = None
    try:
        # 创建并启动容器
        container = self.docker_client.containers.create(**config)
        container.start()
        
        # 等待容器完成，带超时控制
        exit_status = container.wait(timeout=timeout)
        
        if exit_status['StatusCode'] == 0:
            # 正常完成
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8')
            return {"success": True, "stdout": stdout, "stderr": stderr}
        else:
            # 执行失败
            return {"success": False, "error": f"退出码: {exit_status['StatusCode']}"}
            
    except docker.errors.APIError as e:
        if "timeout" in str(e).lower() or "read timed out" in str(e).lower():
            # 超时处理
            try:
                container.kill()  # 强制停止容器
            except:
                pass
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "error": f"代码执行超时（{timeout}秒）"
            }
    finally:
        # 确保容器被清理
        if container:
            try:
                container.remove(force=True)
            except:
                pass
```

### 4. 超时场景处理

#### 4.1 睡眠/等待型超时
```python
# 这种代码会在指定时间后被终止
code = """
import time
time.sleep(10)  # 如果timeout=5，会在5秒后被终止
print("这行不会执行")
"""
```

#### 4.2 CPU密集型超时
```python
# 这种无限循环也会被超时机制终止
code = """
while True:
    x = 1 + 1  # CPU密集型任务
"""
```

#### 4.3 I/O阻塞型超时
```python
# 网络请求或文件I/O阻塞也受超时控制
code = """
import requests
# 如果网络请求hang住，也会被超时终止
response = requests.get('http://httpbin.org/delay/10')
"""
```

### 5. 超时错误处理

#### 5.1 API响应格式
```json
{
  "success": false,
  "stdout": "",
  "stderr": "",
  "execution_time": 3.26,
  "files": {},
  "error": "代码执行超时（3秒）"
}
```

#### 5.2 错误类型识别
- **明确超时错误**: `"代码执行超时（X秒）"`
- **网络超时错误**: 包含"read timed out"的Docker API错误
- **容器超时错误**: Docker容器wait超时

### 6. 性能特性

#### 6.1 精确的时间控制
- **精度**: 秒级精度，通常在±0.1秒范围内
- **响应时间**: 超时触发后立即返回，不会等待额外时间
- **资源清理**: 超时后立即清理Docker容器

#### 6.2 实际测试结果
```
测试场景                    | 设置超时 | 实际耗时 | 状态
---------------------------|---------|---------|--------
正常执行print()            | 10秒    | 0.27秒  | ✅成功
sleep(2)                  | 5秒     | 2.33秒  | ✅成功  
sleep(10)                 | 3秒     | 3.26秒  | ❌超时
无限循环while True         | 2秒     | 2.29秒  | ❌超时
```

### 7. 最佳实践

#### 7.1 timeout设置建议
```python
# 不同类型任务的推荐超时设置
timeout_recommendations = {
    "简单计算": 5,          # 数学计算、字符串处理
    "文件操作": 10,         # 读写小文件
    "数据处理": 30,         # JSON处理、小数据集分析
    "网络请求": 60,         # HTTP请求、API调用
    "大数据处理": 120,      # 大文件处理、复杂计算
    "机器学习": 300,        # 模型训练、预测
}
```

#### 7.2 客户端timeout处理
```python
import requests
import time

def execute_with_retry(code, timeout=30, max_retries=3):
    """带重试的代码执行"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/execute",
                json={"code": code, "timeout": timeout},
                timeout=timeout + 10  # HTTP timeout > 执行timeout
            )
            result = response.json()
            
            if result["success"]:
                return result
            elif "超时" in result.get("error", ""):
                print(f"尝试 {attempt + 1}: 执行超时，增加timeout重试")
                timeout = min(timeout * 2, 300)  # 翻倍但不超过最大值
            else:
                # 非超时错误，不重试
                return result
                
        except requests.exceptions.Timeout:
            print(f"尝试 {attempt + 1}: HTTP请求超时")
            
    return {"success": False, "error": "所有重试都失败了"}
```

### 8. 监控和调试

#### 8.1 超时监控
```python
# 监控超时频率的示例代码
timeout_stats = {
    "total_requests": 0,
    "timeout_count": 0,
    "avg_execution_time": 0
}

def track_execution(result):
    timeout_stats["total_requests"] += 1
    
    if not result["success"] and "超时" in result.get("error", ""):
        timeout_stats["timeout_count"] += 1
    
    timeout_rate = timeout_stats["timeout_count"] / timeout_stats["total_requests"]
    print(f"超时率: {timeout_rate:.2%}")
```

#### 8.2 性能调优
```bash
# 查看Docker容器资源使用
docker stats

# 监控API响应时间
time curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"print(\"test\")", "timeout":10}'
```

---

### 安全策略

1. **代码静态分析**: 使用AST分析检测危险操作
2. **模块导入限制**: 禁止导入系统敏感模块
3. **函数调用限制**: 禁用eval、exec等危险函数
4. **容器隔离**: 使用Docker容器隔离执行环境
5. **资源限制**: 限制内存、CPU使用和执行时间
6. **网络隔离**: 可配置的网络访问控制

### 被禁止的操作

- 系统命令执行 (`os.system`, `subprocess`)
- 文件系统访问 (`open` 限制在工作目录)
- 网络服务启动 (`socket.bind`)
- 进程操作 (`multiprocessing`)
- 动态代码执行 (`eval`, `exec`, `compile`)

---

## 📊 监控和运维

### 日志管理
```bash
# 查看应用日志
docker logs sandbox-api

# 实时查看日志
docker logs -f sandbox-api

# 查看特定时间段日志
docker logs --since "2025-05-29T10:00:00" sandbox-api
```

### 性能监控
```bash
# 查看容器资源使用
docker stats sandbox-api

# 查看系统资源
htop
iostat -x 1
```

### 健康检查
```bash
# API健康检查
curl http://localhost:8000/health

# Docker健康检查
docker ps
```

### 备份和恢复
```bash
# 备份配置
tar -czf backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml .env config/

# 恢复配置
tar -xzf backup-20250529.tar.gz
```

---

## 🧪 测试指南

### 运行所有测试
```bash
./test.sh all
```

### 单独运行测试类型
```bash
./test.sh unit          # 单元测试
./test.sh integration   # 集成测试
./test.sh performance   # 性能测试
./test.sh stress        # 压力测试
```

### 生成测试报告
```bash
./test.sh report
```

报告将生成在 `reports/` 目录中，包括：
- HTML覆盖率报告
- XML测试结果
- 性能测试报告

---

## 🔧 故障排除

### 常见问题

#### 1. Docker连接失败
```bash
# 检查Docker服务状态
sudo systemctl status docker

# 重启Docker服务
sudo systemctl restart docker

# 检查Docker Socket权限
ls -la /var/run/docker.sock
```

#### 2. 端口占用
```bash
# 查看端口占用
lsof -i :8000
netstat -tulpn | grep :8000

# 终止占用进程
kill -9 <PID>
```

#### 3. 权限问题
```bash
# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录或刷新组权限
newgrp docker
```

#### 4. 内存不足
```bash
# 调整Docker容器内存限制
docker run -m 1g python-sandbox

# 修改docker-compose.yml中的内存限制
```

### 调试模式

#### 启用详细日志
```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 启动服务
uvicorn main:app --log-level debug
```

#### 容器内调试
```bash
# 进入容器
docker exec -it sandbox-api bash

# 查看进程
ps aux

# 查看网络
netstat -tulpn
```

---

## 📈 性能优化

### 应用层优化

1. **并发处理**: 使用多worker进程
2. **缓存策略**: 缓存Docker镜像和常用结果
3. **连接池**: 复用Docker客户端连接
4. **异步处理**: 使用异步I/O处理请求

### 系统层优化

1. **资源限制**: 合理设置内存和CPU限制
2. **磁盘I/O**: 使用SSD存储临时文件
3. **网络优化**: 配置网络缓冲区大小
4. **容器优化**: 使用轻量级基础镜像

### 监控指标

- 请求响应时间
- 并发执行数量
- 内存使用率
- CPU使用率
- 磁盘I/O
- 网络吞吐量

---

## 🔮 扩展开发

### 添加新功能

1. **新的安全策略**: 在 `sandbox/security.py` 中添加检查逻辑
2. **新的执行环境**: 支持其他编程语言
3. **新的API端点**: 在 `main.py` 中添加路由
4. **新的中间件**: 添加认证、限流等功能

### 插件系统

```python
# 示例：添加代码格式化插件
class CodeFormatter:
    def format_code(self, code: str) -> str:
        # 实现代码格式化逻辑
        return formatted_code
```

### 自定义配置

```python
# config/custom_settings.py
from .settings import Settings

class CustomSettings(Settings):
    # 添加自定义配置项
    custom_feature_enabled: bool = False
    custom_timeout: int = 60
```

---

## 📞 支持和贡献

### 技术支持

- 📧 邮箱: support@example.com
- 💬 论坛: https://forum.example.com
- 📖 文档: https://docs.example.com
- 🐛 问题反馈: https://github.com/example/issues

### 贡献指南

1. Fork 项目
2. 创建特性分支
3. 编写测试
4. 提交变更
5. 创建 Pull Request

### 开发环境设置

```bash
# 克隆开发版本
git clone https://github.com/example/SimplePySandbox.git
cd SimplePySandbox

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行测试
./test.sh all
```

---

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

## 🎯 路线图

### v1.1 (计划中)
- [ ] 支持更多编程语言 (JavaScript, Go)
- [ ] 添加代码执行历史记录
- [ ] 实现用户认证系统
- [ ] 添加速率限制功能

### v1.2 (规划中)
- [ ] 支持GPU计算
- [ ] 添加代码共享功能
- [ ] 实现实时协作编辑
- [ ] 添加代码版本控制

### v2.0 (长期目标)
- [ ] 微服务架构重构
- [ ] 支持分布式执行
- [ ] 添加机器学习模型训练
- [ ] 实现云原生部署

---

*最后更新: 2025年5月29日*
