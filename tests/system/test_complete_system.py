#!/usr/bin/env python3
"""
完整的系统测试套件
测试SimplePySandbox的所有主要功能
"""

import pytest
import requests
import json
import time
import base64
from datetime import datetime

pytestmark = [pytest.mark.system, pytest.mark.slow, pytest.mark.requires_docker]


class SimplePySandboxTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, message="", details=None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
    
    def test_health_check(self):
        """测试健康检查端点"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("健康检查", True, f"状态: {data['status']}")
                return True
            else:
                self.log_test("健康检查", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("健康检查", False, str(e))
            return False
    
    def test_basic_code_execution(self):
        """测试基本代码执行"""
        try:
            payload = {
                "code": "print('Hello, SimplePySandbox!')",
                "timeout": 10
            }
            response = self.session.post(f"{self.base_url}/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data["success"] and "Hello, SimplePySandbox!" in data["stdout"]:
                    self.log_test("基本代码执行", True, "Hello World 测试通过")
                    return True
                else:
                    self.log_test("基本代码执行", False, "输出不匹配", data)
                    return False
            else:
                self.log_test("基本代码执行", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("基本代码执行", False, str(e))
            return False
    
    def test_math_operations(self):
        """测试数学运算"""
        try:
            code = """
import math
result = math.sqrt(16)
print(f"sqrt(16) = {result}")
print(f"pi = {math.pi}")
print(f"factorial(5) = {math.factorial(5)}")
"""
            payload = {"code": code, "timeout": 10}
            response = self.session.post(f"{self.base_url}/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data["success"] and "sqrt(16) = 4.0" in data["stdout"]:
                    self.log_test("数学运算", True, "数学库测试通过")
                    return True
                else:
                    self.log_test("数学运算", False, "数学运算结果不正确", data)
                    return False
            else:
                self.log_test("数学运算", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("数学运算", False, str(e))
            return False
    
    def test_file_operations(self):
        """测试文件操作"""
        try:
            code = """
# 创建文件
with open("test.txt", "w") as f:
    f.write("Hello from file!")

# 读取文件
with open("test.txt", "r") as f:
    content = f.read()
    print(f"File content: {content}")

# 列出文件
import os
files = os.listdir(".")
print(f"Files: {sorted(files)}")
"""
            payload = {"code": code, "timeout": 10}
            response = self.session.post(f"{self.base_url}/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if (data["success"] and 
                    "Hello from file!" in data["stdout"] and 
                    "test.txt" in data["files"]):
                    self.log_test("文件操作", True, "文件创建和读取成功")
                    return True
                else:
                    self.log_test("文件操作", False, "文件操作失败", data)
                    return False
            else:
                self.log_test("文件操作", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("文件操作", False, str(e))
            return False
    
    def test_error_handling(self):
        """测试错误处理"""
        try:
            # 测试语法错误
            payload = {"code": "print('unclosed string", "timeout": 10}
            response = self.session.post(f"{self.base_url}/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if not data["success"] and "SyntaxError" in data["stderr"]:
                    self.log_test("错误处理-语法错误", True, "语法错误正确捕获")
                else:
                    self.log_test("错误处理-语法错误", False, "语法错误未正确处理", data)
                    return False
            else:
                self.log_test("错误处理-语法错误", False, f"HTTP {response.status_code}")
                return False
            
            # 测试运行时错误
            payload = {"code": "print(1/0)", "timeout": 10}
            response = self.session.post(f"{self.base_url}/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if not data["success"] and "ZeroDivisionError" in data["stderr"]:
                    self.log_test("错误处理-运行时错误", True, "运行时错误正确捕获")
                    return True
                else:
                    self.log_test("错误处理-运行时错误", False, "运行时错误未正确处理", data)
                    return False
            else:
                self.log_test("错误处理-运行时错误", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("错误处理", False, str(e))
            return False
    
    def test_timeout(self):
        """测试超时机制"""
        try:
            code = """
import time
print("Starting sleep...")
time.sleep(5)
print("This should not print")
"""
            payload = {"code": code, "timeout": 2}
            response = self.session.post(f"{self.base_url}/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if (not data["success"] and 
                    "超时" in data.get("error", "") and 
                    data["execution_time"] >= 2):
                    self.log_test("超时机制", True, f"超时正确触发: {data['execution_time']:.2f}s")
                    return True
                else:
                    self.log_test("超时机制", False, "超时未正确触发", data)
                    return False
            else:
                self.log_test("超时机制", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("超时机制", False, str(e))
            return False
    
    def test_environment_management(self):
        """测试环境管理"""
        try:
            # 创建环境
            env_payload = {
                "name": "test-env",
                "description": "测试环境",
                "base_image": "python:3.11-slim",
                "setup_script": "pip install requests",
                "python_version": "3.11"
            }
            response = self.session.post(f"{self.base_url}/environments", json=env_payload)
            
            if response.status_code != 200:
                self.log_test("环境管理-创建", False, f"创建环境失败: HTTP {response.status_code}")
                return False
            
            # 等待环境就绪
            time.sleep(2)
            
            # 列出环境
            response = self.session.get(f"{self.base_url}/environments")
            if response.status_code != 200:
                self.log_test("环境管理-列表", False, f"获取环境列表失败: HTTP {response.status_code}")
                return False
            
            envs = response.json()
            if not any(env["name"] == "test-env" for env in envs["environments"]):
                self.log_test("环境管理-列表", False, "创建的环境未出现在列表中")
                return False
            
            # 在环境中执行代码
            code_payload = {
                "code": "import requests\nprint(f'Requests version: {requests.__version__}')",
                "environment": "test-env",
                "timeout": 15
            }
            response = self.session.post(f"{self.base_url}/execute", json=code_payload)
            
            if response.status_code == 200:
                data = response.json()
                if data["success"] and "Requests version:" in data["stdout"]:
                    self.log_test("环境管理", True, "环境创建和使用成功")
                    return True
                else:
                    self.log_test("环境管理", False, "环境中代码执行失败", data)
                    return False
            else:
                self.log_test("环境管理", False, f"环境中代码执行HTTP错误: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("环境管理", False, str(e))
            return False
    
    def test_input_files(self):
        """测试输入文件功能"""
        try:
            # 创建base64编码的输入文件
            input_content = "Hello from input file!"
            input_b64 = base64.b64encode(input_content.encode()).decode()
            
            code = """
# 读取输入文件
with open("input.txt", "r") as f:
    content = f.read()
    print(f"Input file content: {content}")

# 创建输出文件
with open("output.txt", "w") as f:
    f.write(f"Processed: {content.upper()}")

print("File processing completed")
"""
            
            payload = {
                "code": code,
                "timeout": 10,
                "files": {"input.txt": input_b64}
            }
            response = self.session.post(f"{self.base_url}/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if (data["success"] and 
                    "Hello from input file!" in data["stdout"] and
                    "output.txt" in data["files"]):
                    # 解码输出文件
                    output_content = base64.b64decode(data["files"]["output.txt"]).decode()
                    expected_content = "Processed: HELLO FROM INPUT FILE!"
                    if expected_content in output_content:
                        self.log_test("输入文件处理", True, "文件输入输出成功")
                        return True
                    else:
                        self.log_test("输入文件处理", False, f"输出文件内容不正确: 期望包含'{expected_content}', 实际'{output_content}'")
                        return False
                else:
                    self.log_test("输入文件处理", False, "文件处理失败", data)
                    return False
            else:
                self.log_test("输入文件处理", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("输入文件处理", False, str(e))
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始SimplePySandbox完整系统测试...")
        print("=" * 60)
        
        tests = [
            self.test_health_check,
            self.test_basic_code_execution,
            self.test_math_operations,
            self.test_file_operations,
            self.test_error_handling,
            self.test_timeout,
            self.test_input_files,
            self.test_environment_management
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ 测试异常: {test.__name__} - {e}")
                failed += 1
            print()
        
        print("=" * 60)
        print(f"📊 测试结果总结:")
        print(f"   ✅ 通过: {passed}")
        print(f"   ❌ 失败: {failed}")
        print(f"   📈 成功率: {passed/(passed+failed)*100:.1f}%")
        
        if failed == 0:
            print("🎉 所有测试通过！SimplePySandbox运行正常。")
        else:
            print("⚠️  有测试失败，请检查系统配置。")
        
        return failed == 0


if __name__ == "__main__":
    tester = SimplePySandboxTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
