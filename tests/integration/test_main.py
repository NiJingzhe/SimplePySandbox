import pytest
from fastapi.testclient import TestClient
from main import app
import base64

pytestmark = pytest.mark.integration

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "SimplePySandbox API"


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_simple_code_execution():
    """测试简单代码执行"""
    code = "print('Hello, World!')"
    response = client.post("/execute", json={
        "code": code,
        "timeout": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "Hello, World!" in data["stdout"]
    assert data["stderr"] == ""
    assert data["execution_time"] > 0


def test_code_with_math():
    """测试数学计算"""
    code = """
import math
result = math.sqrt(16)
print(f"Square root of 16 is: {result}")
"""
    response = client.post("/execute", json={
        "code": code,
        "timeout": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "Square root of 16 is: 4.0" in data["stdout"]


def test_code_with_file_creation():
    """测试文件创建"""
    code = """
with open('output.txt', 'w') as f:
    f.write('Hello from sandbox!')
print('File created successfully')
"""
    response = client.post("/execute", json={
        "code": code,
        "timeout": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "File created successfully" in data["stdout"]
    assert "output.txt" in data["files"]
    
    # 验证文件内容
    file_content = base64.b64decode(data["files"]["output.txt"]).decode('utf-8')
    assert file_content == "Hello from sandbox!"


def test_empty_code():
    """测试空代码"""
    response = client.post("/execute", json={
        "code": "",
        "timeout": 10
    })
    
    assert response.status_code == 400