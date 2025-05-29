#!/usr/bin/env python3
"""
SimplePySandbox 高级示例

展示更复杂的用例和最佳实践
"""

import requests
import json
import base64
import time
import concurrent.futures
from typing import List, Dict, Any


class AdvancedSandboxClient:
    """高级沙盒客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def execute_code_batch(self, code_list: List[Dict[str, Any]], max_workers: int = 3):
        """
        批量执行代码
        
        Args:
            code_list: 代码列表，每个元素包含 code, timeout, files 等
            max_workers: 最大并发数
        
        Returns:
            List[Dict]: 执行结果列表
        """
        def execute_single(code_info):
            return self.execute_code(**code_info)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(execute_single, code_list))
        
        return results
    
    def execute_code(self, code: str, timeout: int = 30, files: dict | None = None, metadata: dict | None = None):
        """执行单个代码"""
        files_b64 = {}
        if files:
            for filename, content in files.items():
                if isinstance(content, str):
                    content = content.encode('utf-8')
                files_b64[filename] = base64.b64encode(content).decode('utf-8')
        
        payload = {
            "code": code,
            "timeout": timeout,
            "files": files_b64 if files_b64 else None
        }
        
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/execute",
                json=payload,
                timeout=timeout + 10
            )
            response.raise_for_status()
            result = response.json()
            result["client_execution_time"] = time.time() - start_time
            result["metadata"] = metadata or {}
            return result
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "stdout": "",
                "stderr": "",
                "execution_time": 0,
                "client_execution_time": time.time() - start_time,
                "files": {},
                "metadata": metadata or {}
            }


def example_parallel_processing():
    """并行处理示例"""
    print("=== 并行处理示例 ===")
    
    client = AdvancedSandboxClient()
    
    # 创建多个数据处理任务
    tasks = []
    for i in range(5):
        code = f"""
import json
import math

# 任务 {i+1}: 处理数据集 {i+1}
data_size = {100 + i * 50}
print(f"处理任务 {i+1}，数据大小: {{data_size}}")

# 模拟数据处理
results = []
for j in range(data_size):
    value = math.sin(j * 0.1 + {i}) * 100
    results.append(round(value, 2))

# 统计
stats = {{
    "task_id": {i+1},
    "data_size": data_size,
    "min_value": min(results),
    "max_value": max(results),
    "avg_value": sum(results) / len(results)
}}

print(f"任务 {i+1} 统计: {{json.dumps(stats, indent=2)}}")

# 保存结果
with open(f'task_{i+1}_results.json', 'w') as f:
    json.dump({{
        "stats": stats,
        "sample_data": results[:10]  # 保存前10个数据点
    }}, f, indent=2)

print(f"任务 {i+1} 完成!")
"""
        
        tasks.append({
            "code": code,
            "timeout": 15,
            "metadata": {"task_id": i+1, "task_type": "data_processing"}
        })
    
    print(f"提交 {len(tasks)} 个并行任务...")
    start_time = time.time()
    
    results = client.execute_code_batch(tasks, max_workers=3)
    
    total_time = time.time() - start_time
    print(f"所有任务完成，总耗时: {total_time:.2f}秒")
    
    # 分析结果
    successful_tasks = [r for r in results if r["success"]]
    failed_tasks = [r for r in results if not r["success"]]
    
    print(f"成功: {len(successful_tasks)}, 失败: {len(failed_tasks)}")
    
    if successful_tasks:
        avg_execution_time = sum(r["execution_time"] for r in successful_tasks) / len(successful_tasks)
        print(f"平均执行时间: {avg_execution_time:.3f}秒")
        
        # 显示每个任务的结果
        for result in successful_tasks:
            task_id = result["metadata"]["task_id"]
            files = result["files"]
            print(f"任务 {task_id}: 生成 {len(files)} 个文件")
    
    if failed_tasks:
        print("失败的任务:")
        for result in failed_tasks:
            task_id = result["metadata"]["task_id"]
            print(f"  任务 {task_id}: {result['error']}")


def example_streaming_simulation():
    """流式处理模拟"""
    print("\n=== 流式处理模拟 ===")
    
    client = AdvancedSandboxClient()
    
    # 模拟流式数据处理
    batch_size = 3
    total_batches = 5
    
    print(f"模拟 {total_batches} 个批次的流式处理，每批次 {batch_size} 个任务")
    
    all_results = []
    
    for batch_idx in range(total_batches):
        print(f"\n处理批次 {batch_idx + 1}/{total_batches}")
        
        # 创建当前批次的任务
        batch_tasks = []
        for i in range(batch_size):
            global_task_id = batch_idx * batch_size + i + 1
            
            code = f"""
import json
import time
import random

# 模拟流式数据处理
task_id = {global_task_id}
batch_id = {batch_idx + 1}

print(f"开始处理流式任务 {{task_id}} (批次 {{batch_id}})")

# 模拟接收数据
data_points = []
for i in range(50):
    # 模拟实时数据
    timestamp = time.time() + i * 0.1
    value = random.uniform(0, 100) + 20 * math.sin(i * 0.2)
    data_points.append({{"timestamp": timestamp, "value": round(value, 2)}})

print(f"收到 {{len(data_points)}} 个数据点")

# 实时分析
window_size = 10
moving_averages = []

for i in range(len(data_points) - window_size + 1):
    window = data_points[i:i + window_size]
    avg = sum(point["value"] for point in window) / window_size
    moving_averages.append(round(avg, 2))

# 异常检测
anomalies = []
if moving_averages:
    threshold = 1.5 * (max(moving_averages) - min(moving_averages)) / 2
    baseline = sum(moving_averages) / len(moving_averages)
    
    for i, avg in enumerate(moving_averages):
        if abs(avg - baseline) > threshold:
            anomalies.append({{
                "index": i,
                "value": avg,
                "deviation": round(abs(avg - baseline), 2)
            }})

print(f"检测到 {{len(anomalies)}} 个异常点")

# 保存结果
result = {{
    "task_id": task_id,
    "batch_id": batch_id,
    "data_count": len(data_points),
    "moving_avg_count": len(moving_averages),
    "anomaly_count": len(anomalies),
    "summary": {{
        "min_value": min(point["value"] for point in data_points),
        "max_value": max(point["value"] for point in data_points),
        "avg_value": sum(point["value"] for point in data_points) / len(data_points)
    }}
}}

with open(f'stream_task_{{task_id}}.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"流式任务 {{task_id}} 处理完成")
"""
            
            batch_tasks.append({
                "code": code,
                "timeout": 20,
                "metadata": {
                    "task_id": global_task_id,
                    "batch_id": batch_idx + 1,
                    "task_type": "streaming"
                }
            })
        
        # 执行当前批次
        batch_results = client.execute_code_batch(batch_tasks, max_workers=batch_size)
        all_results.extend(batch_results)
        
        # 显示批次结果
        successful = sum(1 for r in batch_results if r["success"])
        print(f"批次 {batch_idx + 1} 完成: {successful}/{len(batch_tasks)} 成功")
        
        # 模拟批次间隔
        if batch_idx < total_batches - 1:
            time.sleep(1)
    
    # 汇总所有结果
    print(f"\n流式处理完成!")
    successful_results = [r for r in all_results if r["success"]]
    print(f"总体成功率: {len(successful_results)}/{len(all_results)} ({100*len(successful_results)/len(all_results):.1f}%)")
    
    if successful_results:
        total_execution_time = sum(r["execution_time"] for r in successful_results)
        print(f"总执行时间: {total_execution_time:.2f}秒")
        
        # 分析生成的文件
        total_files = sum(len(r["files"]) for r in successful_results)
        print(f"总共生成 {total_files} 个文件")


def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    client = AdvancedSandboxClient()
    
    # 测试各种错误情况
    error_cases = [
        {
            "name": "语法错误",
            "code": "print('missing quote",
            "timeout": 10
        },
        {
            "name": "运行时错误",
            "code": "x = 1 / 0",
            "timeout": 10
        },
        {
            "name": "导入错误",
            "code": "import nonexistent_module",
            "timeout": 10
        },
        {
            "name": "超时测试",
            "code": "import time\ntime.sleep(20)",
            "timeout": 5
        },
        {
            "name": "内存密集型（可能触发限制）",
            "code": "big_list = [i for i in range(10**7)]",
            "timeout": 15
        }
    ]
    
    for case in error_cases:
        print(f"\n测试: {case['name']}")
        result = client.execute_code(
            case["code"], 
            timeout=case["timeout"],
            metadata={"test_case": case["name"]}
        )
        
        if result["success"]:
            print(f"  ✅ 意外成功 (执行时间: {result['execution_time']:.3f}s)")
            if result["stdout"]:
                print(f"  输出: {result['stdout'][:100]}...")
        else:
            print(f"  ❌ 预期失败: {result['error']}")
            if result["stderr"]:
                print(f"  错误详情: {result['stderr'][:100]}...")
        
        print(f"  客户端耗时: {result['client_execution_time']:.3f}s")


def example_performance_benchmark():
    """性能基准测试"""
    print("\n=== 性能基准测试 ===")
    
    client = AdvancedSandboxClient()
    
    # 不同复杂度的测试用例
    benchmark_cases = [
        {
            "name": "简单计算",
            "code": "result = sum(range(1000))\nprint(f'Result: {result}')",
            "expected_time": 0.1
        },
        {
            "name": "文件操作",
            "code": """
data = '\\n'.join([f'line {i}' for i in range(1000)])
with open('test.txt', 'w') as f:
    f.write(data)
with open('test.txt', 'r') as f:
    lines = f.readlines()
print(f'Processed {len(lines)} lines')
""",
            "expected_time": 0.2
        },
        {
            "name": "JSON处理",
            "code": """
import json
data = [{'id': i, 'value': i**2} for i in range(1000)]
json_str = json.dumps(data)
parsed = json.loads(json_str)
with open('data.json', 'w') as f:
    json.dump(parsed, f)
print(f'Processed {len(parsed)} records')
""",
            "expected_time": 0.3
        }
    ]
    
    print("运行性能基准测试...")
    
    for case in benchmark_cases:
        print(f"\n测试: {case['name']}")
        
        # 运行多次取平均值
        runs = 3
        times = []
        
        for run in range(runs):
            result = client.execute_code(case["code"], timeout=30)
            if result["success"]:
                times.append(result["execution_time"])
            else:
                print(f"  运行 {run+1} 失败: {result['error']}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"  平均时间: {avg_time:.3f}s")
            print(f"  时间范围: {min_time:.3f}s - {max_time:.3f}s")
            print(f"  预期时间: {case['expected_time']:.3f}s")
            
            if avg_time <= case['expected_time'] * 2:
                print(f"  ✅ 性能符合预期")
            else:
                print(f"  ⚠️  性能可能需要优化")
        else:
            print(f"  ❌ 所有运行都失败了")


def main():
    """主函数"""
    print("SimplePySandbox 高级示例")
    print("=" * 60)
    
    client = AdvancedSandboxClient()
    
    # 健康检查
    try:
        response = client.session.get(f"{client.base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务状态正常")
        else:
            print(f"❌ 服务状态异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        return
    
    try:
        # 运行高级示例
        example_parallel_processing()
        time.sleep(2)
        
        example_streaming_simulation()
        time.sleep(2)
        
        example_error_handling()
        time.sleep(2)
        
        example_performance_benchmark()
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n运行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n高级示例运行完成!")


if __name__ == "__main__":
    main()