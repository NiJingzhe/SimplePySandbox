#!/usr/bin/env python3
"""
测试API层面的timeout机制
"""
import pytest
import requests
import time
import json

pytestmark = [pytest.mark.integration, pytest.mark.slow, pytest.mark.requires_docker]

def test_api_timeout():
    """测试API的timeout功能"""
    base_url = "http://localhost:8000"
    
    print("=== 测试API层面的timeout机制 ===")
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务未运行，请先启动服务")
            print("运行命令: ./start.sh dev")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务，请先启动服务")
        print("运行命令: ./start.sh dev")
        return
    
    print("✅ 服务正在运行")
    
    # 测试1: 正常执行（快速）
    print("\n1. 测试正常执行（快速）")
    start_time = time.time()
    try:
        response = requests.post(f"{base_url}/execute", json={
            "code": "print('Hello from API!')",
            "timeout": 10
        }, timeout=15)
        result = response.json()
        api_time = time.time() - start_time
        
        print(f"  HTTP状态码: {response.status_code}")
        print(f"  成功: {result.get('success', False)}")
        print(f"  输出: {result.get('stdout', '').strip()}")
        print(f"  执行时间: {result.get('execution_time', 0):.2f}s")
        print(f"  API总时间: {api_time:.2f}s")
        print(f"  错误: {result.get('error', 'None')}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
    
    # 测试2: 使用默认timeout
    print("\n2. 测试默认timeout（应该使用30秒）")
    start_time = time.time()
    try:
        response = requests.post(f"{base_url}/execute", json={
            "code": "import time; time.sleep(1); print('使用默认timeout')"
        }, timeout=35)
        result = response.json()
        api_time = time.time() - start_time
        
        print(f"  HTTP状态码: {response.status_code}")
        print(f"  成功: {result.get('success', False)}")
        print(f"  输出: {result.get('stdout', '').strip()}")
        print(f"  执行时间: {result.get('execution_time', 0):.2f}s")
        print(f"  API总时间: {api_time:.2f}s")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
    
    # 测试3: 短timeout（应该超时）
    print("\n3. 测试短timeout（应该超时）")
    start_time = time.time()
    try:
        response = requests.post(f"{base_url}/execute", json={
            "code": "import time; time.sleep(5); print('不应该看到这个')",
            "timeout": 2
        }, timeout=10)
        result = response.json()
        api_time = time.time() - start_time
        
        print(f"  HTTP状态码: {response.status_code}")
        print(f"  成功: {result.get('success', False)}")
        print(f"  输出: '{result.get('stdout', '').strip()}'")
        print(f"  执行时间: {result.get('execution_time', 0):.2f}s")
        print(f"  API总时间: {api_time:.2f}s")
        print(f"  错误: {result.get('error', 'None')}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
    
    # 测试4: 超过最大timeout限制
    print("\n4. 测试超过最大timeout限制（应该被拒绝）")
    try:
        response = requests.post(f"{base_url}/execute", json={
            "code": "print('Hello')",
            "timeout": 500  # 超过MAX_TIMEOUT=300
        }, timeout=10)
        
        print(f"  HTTP状态码: {response.status_code}")
        if response.status_code == 400:
            result = response.json()
            print(f"  ✅ 正确拒绝: {result.get('detail', 'Unknown error')}")
        else:
            result = response.json()
            print(f"  ⚠️ 意外结果: {result}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
    
    # 测试5: 无限循环（CPU密集型超时）
    print("\n5. 测试无限循环（CPU密集型超时）")
    start_time = time.time()
    try:
        response = requests.post(f"{base_url}/execute", json={
            "code": "while True: x = 1 + 1",
            "timeout": 3
        }, timeout=10)
        result = response.json()
        api_time = time.time() - start_time
        
        print(f"  HTTP状态码: {response.status_code}")
        print(f"  成功: {result.get('success', False)}")
        print(f"  输出: '{result.get('stdout', '').strip()}'")
        print(f"  执行时间: {result.get('execution_time', 0):.2f}s")
        print(f"  API总时间: {api_time:.2f}s")
        print(f"  错误: {result.get('error', 'None')}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")

if __name__ == "__main__":
    test_api_timeout()
