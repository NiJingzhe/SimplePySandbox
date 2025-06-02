#!/usr/bin/env python3
"""
SimplePySandbox 客户端示例
演示如何与SimplePySandbox API进行交互
"""

import requests
import json
import time
import base64
from typing import Dict, Any, Optional


class SimplePySandboxClient:
    """SimplePySandbox API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: API服务器地址
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """检查服务健康状态"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def execute_code(self, 
                    code: str, 
                    timeout: int = 10, 
                    environment: Optional[str] = None) -> Dict[str, Any]:
        """
        执行Python代码
        
        Args:
            code: 要执行的Python代码
            timeout: 超时时间（秒）
            environment: 指定执行环境（可选）
            
        Returns:
            执行结果字典
        """
        payload = {
            "code": code,
            "timeout": timeout
        }
        
        if environment:
            payload["environment"] = environment
        
        response = self.session.post(
            f"{self.base_url}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def list_environments(self) -> Dict[str, Any]:
        """列出所有可用环境"""
        response = self.session.get(f"{self.base_url}/environments")
        response.raise_for_status()
        return response.json()
    
    def create_environment(self, 
                          name: str, 
                          setup_script: str,
                          description: str = "",
                          python_version: str = "3.11") -> Dict[str, Any]:
        """
        创建新环境
        
        Args:
            name: 环境名称
            setup_script: 设置脚本
            description: 环境描述
            python_version: Python版本
            
        Returns:
            创建结果
        """
        payload = {
            "name": name,
            "description": description,
            "setup_script": setup_script,
            "python_version": python_version
        }
        
        response = self.session.post(
            f"{self.base_url}/environments",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_environment(self, name: str) -> Dict[str, Any]:
        """删除环境"""
        response = self.session.delete(f"{self.base_url}/environments/{name}")
        response.raise_for_status()
        return response.json()
    
    def decode_file(self, encoded_content: str) -> str:
        """解码base64编码的文件内容"""
        return base64.b64decode(encoded_content).decode('utf-8')
    
    def print_result(self, result: Dict[str, Any]) -> None:
        """美化打印执行结果"""
        print("=" * 50)
        print(f"执行状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        
        if result['stdout']:
            print("\n📤 标准输出:")
            print(result['stdout'])
        
        if result['stderr']:
            print("\n⚠️ 错误输出:")
            print(result['stderr'])
        
        if result['error']:
            print(f"\n❌ 错误信息: {result['error']}")
        
        if result['files']:
            print(f"\n📁 生成文件 ({len(result['files'])}个):")
            for filename, content in result['files'].items():
                print(f"  📄 {filename}")
                try:
                    decoded = self.decode_file(content)
                    print(f"     内容预览: {decoded[:100]}...")
                except:
                    print(f"     大小: {len(content)} 字符 (base64)")
        
        print("=" * 50)


def demo_basic_usage():
    """演示基本用法"""
    print("🚀 SimplePySandbox 客户端演示")
    
    # 创建客户端
    client = SimplePySandboxClient()
    
    # 健康检查
    print("\n1. 健康检查...")
    try:
        health = client.health_check()
        print(f"✅ 服务状态: {health['status']}")
        print(f"📅 时间戳: {health['timestamp']}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 基本代码执行
    print("\n2. 基本代码执行...")
    basic_code = """
print("Hello from SimplePySandbox!")
import sys
print(f"Python版本: {sys.version}")

# 简单计算
numbers = [1, 2, 3, 4, 5]
result = sum(x**2 for x in numbers)
print(f"平方和: {result}")
"""
    
    result = client.execute_code(basic_code)
    client.print_result(result)


def demo_file_operations():
    """演示文件操作"""
    print("\n3. 文件操作演示...")
    
    client = SimplePySandboxClient()
    
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

# 创建文本文件
with open("readme.txt", "w", encoding="utf-8") as f:
    f.write("SimplePySandbox文件操作演示\\n")
    f.write("=" * 30 + "\\n")
    f.write("这是一个测试文件\\n")
    f.write(f"创建时间: {datetime.now()}\\n")

print("✅ 所有文件创建完成!")
print(f"📁 当前目录文件: {os.listdir('.')}")
"""
    
    result = client.execute_code(file_code)
    client.print_result(result)


def demo_performance_test():
    """演示性能测试"""
    print("\n4. 性能测试演示...")
    
    client = SimplePySandboxClient()
    
    perf_code = """
import time
import math

print("🔥 性能测试开始...")

# 测试1: 数学计算
start = time.time()
result = sum(math.sqrt(i) for i in range(10000))
math_time = time.time() - start
print(f"数学计算: {result:.2f}, 耗时: {math_time:.3f}秒")

# 测试2: 字符串操作
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

# 测试3: 列表操作
start = time.time()
numbers = list(range(50000))
processed = [x**2 for x in numbers if x % 2 == 0]
list_time = time.time() - start
print(f"列表操作: 处理{len(processed)}个元素, 耗时: {list_time:.3f}秒")

print("✅ 性能测试完成!")
"""
    
    result = client.execute_code(perf_code, timeout=20)
    client.print_result(result)


def demo_error_handling():
    """演示错误处理"""
    print("\n5. 错误处理演示...")
    
    client = SimplePySandboxClient()
    
    # 语法错误
    print("5.1 语法错误测试...")
    syntax_error_code = """
print("语法错误测试")
if True
    print("缺少冒号")
"""
    
    result = client.execute_code(syntax_error_code)
    client.print_result(result)
    
    # 运行时错误
    print("\\n5.2 运行时错误测试...")
    runtime_error_code = """
print("运行时错误测试")
x = 10
y = 0
result = x / y  # 除零错误
print(f"结果: {result}")
"""
    
    result = client.execute_code(runtime_error_code)
    client.print_result(result)
    
    # 超时测试
    print("\\n5.3 超时测试...")
    timeout_code = """
import time
print("开始长时间操作...")
time.sleep(5)  # 睡眠5秒，但超时设置为2秒
print("操作完成")
"""
    
    result = client.execute_code(timeout_code, timeout=2)
    client.print_result(result)


def demo_environment_management():
    """演示环境管理"""
    print("\n6. 环境管理演示...")
    
    client = SimplePySandboxClient()
    
    # 列出环境
    print("6.1 列出现有环境...")
    try:
        envs = client.list_environments()
        print(f"📦 发现 {envs['total']} 个环境:")
        for env in envs['environments']:
            print(f"  - {env['name']}: {env['description']} ({env['status']})")
    except Exception as e:
        print(f"❌ 获取环境列表失败: {e}")
    
    # 尝试创建环境
    print("\\n6.2 创建测试环境...")
    try:
        setup_script = """
pip install requests beautifulsoup4
echo "测试环境设置完成"
"""
        result = client.create_environment(
            name="demo-env",
            description="演示环境",
            setup_script=setup_script
        )
        print("✅ 环境创建成功")
    except Exception as e:
        print(f"⚠️ 环境创建失败: {e}")


if __name__ == "__main__":
    print("🎯 SimplePySandbox API 客户端演示程序")
    print("请确保SimplePySandbox服务正在运行 (http://localhost:8000)")
    
    try:
        demo_basic_usage()
        demo_file_operations()
        demo_performance_test()
        demo_error_handling()
        demo_environment_management()
        
        print("\\n🎉 所有演示完成!")
        print("\\n💡 提示:")
        print("- 查看API文档: http://localhost:8000/docs")
        print("- 健康检查: http://localhost:8000/health")
        print("- 更多示例请查看项目文档")
        
    except KeyboardInterrupt:
        print("\\n👋 演示被用户中断")
    except Exception as e:
        print(f"\\n❌ 演示过程中出现错误: {e}")
        print("请检查SimplePySandbox服务是否正常运行")
