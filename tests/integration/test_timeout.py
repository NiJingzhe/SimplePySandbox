#!/usr/bin/env python3
"""
测试timeout机制
"""
import pytest
import asyncio
import time
from sandbox.executor import CodeExecutor

pytestmark = [pytest.mark.integration, pytest.mark.slow]

async def test_timeout_mechanism():
    """测试超时机制"""
    print("=== 测试timeout机制 ===")
    
    executor = CodeExecutor()
    
    # 测试1: 正常执行（不超时）
    print("\n1. 测试正常执行（不超时）")
    start_time = time.time()
    result = await executor.execute(
        code='print("Hello, World!")',
        timeout=10
    )
    exec_time = time.time() - start_time
    
    print(f"  成功: {result.success}")
    print(f"  输出: {result.stdout.strip()}")
    print(f"  执行时间: {result.execution_time:.2f}s")
    print(f"  总时间: {exec_time:.2f}s")
    print(f"  错误: {result.error}")
    
    # 测试2: 短时间睡眠（不超时）
    print("\n2. 测试短时间睡眠（不超时）")
    start_time = time.time()
    result = await executor.execute(
        code='import time; time.sleep(2); print("短睡眠完成")',
        timeout=5
    )
    exec_time = time.time() - start_time
    
    print(f"  成功: {result.success}")
    print(f"  输出: {result.stdout.strip()}")
    print(f"  执行时间: {result.execution_time:.2f}s")
    print(f"  总时间: {exec_time:.2f}s")
    print(f"  错误: {result.error}")
    
    # 测试3: 长时间睡眠（应该超时）
    print("\n3. 测试长时间睡眠（应该超时）")
    start_time = time.time()
    result = await executor.execute(
        code='import time; time.sleep(10); print("不应该看到这个")',
        timeout=3
    )
    exec_time = time.time() - start_time
    
    print(f"  成功: {result.success}")
    print(f"  输出: '{result.stdout.strip()}'")
    print(f"  执行时间: {result.execution_time:.2f}s")
    print(f"  总时间: {exec_time:.2f}s")
    print(f"  错误: {result.error}")
    
    # 测试4: 无限循环（应该超时）
    print("\n4. 测试无限循环（应该超时）")
    start_time = time.time()
    result = await executor.execute(
        code='while True: pass',
        timeout=2
    )
    exec_time = time.time() - start_time
    
    print(f"  成功: {result.success}")
    print(f"  输出: '{result.stdout.strip()}'")
    print(f"  执行时间: {result.execution_time:.2f}s")
    print(f"  总时间: {exec_time:.2f}s")
    print(f"  错误: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_timeout_mechanism())
