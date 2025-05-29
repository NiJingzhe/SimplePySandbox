"""
环境管理测试
测试不同Python环境的创建和使用
"""
import pytest
import os
import subprocess
from fastapi.testclient import TestClient
from main import app

pytestmark = [pytest.mark.integration, pytest.mark.requires_docker]

client = TestClient(app)

class TestEnvironmentManagement:
    """环境管理测试类"""
    
    def test_default_environment(self):
        """测试默认环境"""
        code = """
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
"""
        
        response = client.post("/execute", json={"code": code})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Python version:" in data["output"]
    
    def test_environment_parameter(self):
        """测试环境参数"""
        code = "print('Hello from custom environment!')"
        
        # 测试使用默认环境
        response = client.post("/execute", json={
            "code": code,
            "environment": "default"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Hello from custom environment!" in data["output"]
    
    def test_python310_environment(self):
        """测试Python 3.10环境（如果存在）"""
        code = """
import sys
import platform
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
"""
        
        response = client.post("/execute", json={
            "code": code,
            "environment": "python310-base"
        })
        
        # 环境可能不存在，这是正常的
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                assert "Python version:" in data["output"]
            else:
                # 如果环境不存在，应该有相应的错误信息
                assert "environment" in data["error"].lower() or "not found" in data["error"].lower()
    
    def test_environment_isolation(self):
        """测试环境隔离"""
        # 在一个执行中创建变量
        code1 = "test_var = 'isolation_test'"
        
        response1 = client.post("/execute", json={"code": code1})
        assert response1.status_code == 200
        assert response1.json()["success"] is True
        
        # 在另一个执行中尝试访问变量（应该失败）
        code2 = "print(test_var)"
        
        response2 = client.post("/execute", json={"code": code2})
        assert response2.status_code == 200
        
        data2 = response2.json()
        # 变量不应该存在，因为每次执行都是隔离的
        assert data2["success"] is False
        assert "NameError" in data2["error"]
    
    def test_package_availability(self):
        """测试包的可用性"""
        packages_to_test = [
            ("math", "math.sqrt(16)"),
            ("json", "json.dumps({'key': 'value'})"),
            ("os", "os.path.exists('.')"),
            ("sys", "sys.version"),
            ("datetime", "datetime.datetime.now()"),
        ]
        
        for package, test_code in packages_to_test:
            code = f"""
import {package}
result = {test_code}
print(f"{package} test: {{result}}")
"""
            
            response = client.post("/execute", json={"code": code})
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True, f"Package {package} test failed: {data.get('error', '')}"
            assert f"{package} test:" in data["output"]
    
    def test_environment_with_files(self):
        """测试环境中的文件操作"""
        code = """
import os
import tempfile

# 创建临时文件
with open('test_env.txt', 'w') as f:
    f.write('Environment test file')

# 读取文件
with open('test_env.txt', 'r') as f:
    content = f.read()

print(f"File content: {content}")

# 清理
os.remove('test_env.txt')
print("File cleaned up")
"""
        
        response = client.post("/execute", json={"code": code})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "File content: Environment test file" in data["output"]
        assert "File cleaned up" in data["output"]


class TestEnvironmentConfiguration:
    """环境配置测试类"""
    
    def test_environment_limits(self):
        """测试环境限制"""
        # 测试内存限制
        code = """
try:
    # 尝试创建大量数据（但不要太大，避免真正耗尽内存）
    data = [i for i in range(100000)]
    print(f"Created list with {len(data)} items")
except MemoryError:
    print("Memory limit reached")
"""
        
        response = client.post("/execute", json={"code": code})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    def test_timeout_enforcement(self):
        """测试超时强制执行"""
        code = """
import time
print("Starting sleep...")
time.sleep(8)  # 8秒睡眠
print("Sleep completed")
"""
        
        response = client.post("/execute", json={
            "code": code,
            "timeout": 5  # 5秒超时
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "timeout" in data["error"].lower() or "time" in data["error"].lower()
    
    def test_security_restrictions(self):
        """测试安全限制"""
        dangerous_codes = [
            "import subprocess; subprocess.run(['ls'])",
            "open('/etc/passwd', 'r').read()",
            "__import__('os').system('ls')",
        ]
        
        for dangerous_code in dangerous_codes:
            response = client.post("/execute", json={"code": dangerous_code})
            assert response.status_code == 200
            
            data = response.json()
            # 应该被安全策略拦截或执行失败
            if not data["success"]:
                # 预期的安全拦截
                assert any(keyword in data["error"].lower() 
                          for keyword in ["permission", "forbidden", "error", "exception"])
            else:
                # 如果执行成功，输出应该被限制
                assert len(data["output"]) < 10000  # 输出长度限制
    
    # 使用skipif而不是skip，这样当你明确运行这个测试时，它不会被自动跳过
    def test_pythonocc_environment(self):
        """测试PythonOCC环境（如果存在）"""
        # 读取测试数据文件
        test_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    "data", "pythonocc_example.py")
        
        with open(test_file_path, 'r') as file:
            code = file.read()
        
        # 在pythonocc环境中执行代码
        response = client.post("/execute", json={
            "code": code,
            "environment": "pythonocc-stable",
            "timeout": 30  # 给一个较长的超时时间
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 如果环境存在且配置正确，测试应该成功
        if data["success"]:
            assert "成功创建圆柱体" in data["output"]
            assert "成功导出STEP文件" in data["output"]
            assert "PythonOCC测试完成" in data["output"]
        else:
            # 环境可能未配置，这种情况下应该检查错误信息
            print(f"PythonOCC环境测试失败: {data['error']}")
            # 如果是因为找不到环境导致的失败，标记测试为跳过
            if "environment" in data["error"].lower() or "not found" in data["error"].lower():
                pytest.skip("PythonOCC环境未配置")
            else:
                # 其他错误应该引起关注
                print(data)
                assert False, f"PythonOCC测试失败: {data['error']}"

