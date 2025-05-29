"""
性能测试套件
测试SimplePySandbox的性能表现
"""
import pytest
import time
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from main import app

pytestmark = [pytest.mark.performance, pytest.mark.slow]

client = TestClient(app)

class TestPerformance:
    """性能测试类"""
    
    def test_single_execution_performance(self):
        """测试单次执行性能"""
        code = "result = sum(range(1000))\nprint(result)"
        
        # 预热
        for _ in range(3):
            client.post("/execute", json={"code": code})
        
        # 测试多次执行时间
        times = []
        for _ in range(10):
            start = time.time()
            response = client.post("/execute", json={"code": code})
            end = time.time()
            
            assert response.status_code == 200
            times.append(end - start)
        
        # 统计分析
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\n性能统计:")
        print(f"平均执行时间: {avg_time:.3f}s")
        print(f"最长执行时间: {max_time:.3f}s")
        print(f"最短执行时间: {min_time:.3f}s")
        
        # 断言性能要求
        assert avg_time < 5.0, f"平均执行时间过长: {avg_time:.3f}s"
        assert max_time < 10.0, f"最长执行时间过长: {max_time:.3f}s"
    
    def test_concurrent_execution_performance(self):
        """测试并发执行性能"""
        code = "import time\ntime.sleep(0.1)\nprint('done')"
        
        def execute_code():
            response = client.post("/execute", json={"code": code})
            return response.status_code == 200
        
        # 测试并发执行
        start = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_code) for _ in range(10)]
            results = [f.result() for f in futures]
        end = time.time()
        
        total_time = end - start
        
        print(f"\n并发性能统计:")
        print(f"10个并发任务总时间: {total_time:.3f}s")
        print(f"成功率: {sum(results)}/{len(results)}")
        
        # 断言性能要求
        assert all(results), "并发执行失败"
        assert total_time < 15.0, f"并发执行时间过长: {total_time:.3f}s"
    
    def test_memory_usage_performance(self):
        """测试内存使用性能"""
        # 创建大量数据的代码
        code = """
import sys
data = list(range(100000))
result = sum(data)
print(f"Result: {result}")
print(f"Memory usage: {sys.getsizeof(data)} bytes")
"""
        
        response = client.post("/execute", json={"code": code})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Result:" in data["output"]
    
    def test_file_operations_performance(self):
        """测试文件操作性能"""
        code = """
import os
import time

# 创建多个文件
start = time.time()
for i in range(100):
    with open(f'test_{i}.txt', 'w') as f:
        f.write(f'Content {i}' * 100)

# 读取文件
content_sum = 0
for i in range(100):
    with open(f'test_{i}.txt', 'r') as f:
        content_sum += len(f.read())

# 清理文件
for i in range(100):
    os.remove(f'test_{i}.txt')

end = time.time()
print(f"File operations took: {end - start:.3f}s")
print(f"Total content size: {content_sum}")
"""
        
        start = time.time()
        response = client.post("/execute", json={"code": code})
        end = time.time()
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        total_time = end - start
        print(f"\n文件操作性能: {total_time:.3f}s")
        assert total_time < 30.0, f"文件操作时间过长: {total_time:.3f}s"
    
    @pytest.mark.slow
    def test_long_running_code_performance(self):
        """测试长时间运行代码的性能"""
        code = """
import time
result = 0
for i in range(1000000):
    result += i
    if i % 100000 == 0:
        print(f"Progress: {i/1000000*100:.1f}%")
print(f"Final result: {result}")
"""
        
        start = time.time()
        response = client.post("/execute", json={
            "code": code,
            "timeout": 30
        })
        end = time.time()
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        execution_time = end - start
        print(f"\n长时间执行性能: {execution_time:.3f}s")
        assert execution_time < 35.0, f"长时间执行超时: {execution_time:.3f}s"
