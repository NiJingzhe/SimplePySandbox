#!/usr/bin/env python3
"""
SimplePySandbox 客户端示例

这个示例展示了如何使用SimplePySandbox API执行Python代码
"""

import requests
import json
import base64
import time


class SandboxClient:
    """沙盒客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def execute_code(self, code: str, timeout: int = 30, files: dict | None = None):
        """
        执行Python代码
        
        Args:
            code: Python代码
            timeout: 超时时间（秒）
            files: 输入文件字典 {filename: content}
        
        Returns:
            dict: 执行结果
        """
        # 准备文件数据
        files_b64 = {}
        if files:
            for filename, content in files.items():
                if isinstance(content, str):
                    content = content.encode('utf-8')
                files_b64[filename] = base64.b64encode(content).decode('utf-8')
        
        # 发送请求
        payload = {
            "code": code,
            "timeout": timeout,
            "files": files_b64 if files_b64 else None
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/execute",
                json=payload,
                timeout=timeout + 10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "stdout": "",
                "stderr": "",
                "execution_time": 0,
                "files": {}
            }
    
    def health_check(self):
        """健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}


def example_basic_execution():
    """基本代码执行示例"""
    print("=== 基本代码执行示例 ===")
    
    client = SandboxClient()
    
    code = """
import math
import json

# 计算数学表达式
result = math.sqrt(16) + math.pi
print(f"计算结果: {result:.2f}")

# 处理数据
data = {"numbers": [1, 2, 3, 4, 5]}
squared = [x**2 for x in data["numbers"]]
print(f"平方数: {squared}")

# 输出JSON
output = {"result": result, "squared": squared}
print(f"JSON输出: {json.dumps(output, indent=2)}")
"""
    
    result = client.execute_code(code, timeout=10)
    
    if result["success"]:
        print("✅ 执行成功!")
        print(f"输出:\n{result['stdout']}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
    else:
        print("❌ 执行失败!")
        print(f"错误: {result['error']}")
        if result['stderr']:
            print(f"错误输出:\n{result['stderr']}")


def example_file_processing():
    """文件处理示例"""
    print("\n=== 文件处理示例 ===")
    
    client = SandboxClient()
    
    # 准备输入文件
    input_files = {
        "data.txt": "apple,banana,cherry\norange,grape,kiwi\n",
        "config.json": json.dumps({"separator": ",", "output_format": "uppercase"})
    }
    
    code = """
import json

# 读取配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

print(f"配置: {config}")

# 读取数据文件
with open('data.txt', 'r') as f:
    lines = f.readlines()

print(f"读取到 {len(lines)} 行数据")

# 处理数据
processed_data = []
for line in lines:
    items = line.strip().split(config['separator'])
    if config['output_format'] == 'uppercase':
        items = [item.upper() for item in items]
    processed_data.append(items)

print(f"处理后的数据: {processed_data}")

# 写入结果文件
with open('result.txt', 'w') as f:
    for items in processed_data:
        f.write(' | '.join(items) + '\\n')

# 写入统计文件
with open('stats.json', 'w') as f:
    stats = {
        "total_lines": len(lines),
        "total_items": sum(len(items) for items in processed_data),
        "processing_config": config
    }
    json.dump(stats, f, indent=2)

print("文件处理完成!")
"""
    
    result = client.execute_code(code, timeout=15, files=input_files)
    
    if result["success"]:
        print("✅ 文件处理成功!")
        print(f"输出:\n{result['stdout']}")
        
        # 显示生成的文件
        print(f"\n生成了 {len(result['files'])} 个文件:")
        for filename, content_b64 in result["files"].items():
            content = base64.b64decode(content_b64).decode('utf-8')
            print(f"\n📄 {filename}:")
            print(content[:200] + ("..." if len(content) > 200 else ""))
    else:
        print("❌ 文件处理失败!")
        print(f"错误: {result['error']}")


def example_data_analysis():
    """数据分析示例"""
    print("\n=== 数据分析示例 ===")
    
    client = SandboxClient()
    
    code = """
import json
import math
from collections import Counter

# 模拟数据生成
data = []
for i in range(100):
    score = 50 + 30 * math.sin(i * 0.1) + (i % 10) * 2
    data.append({
        "id": i + 1,
        "score": round(score, 2),
        "category": ["A", "B", "C"][i % 3]
    })

print(f"生成了 {len(data)} 条数据")

# 统计分析
scores = [item["score"] for item in data]
categories = [item["category"] for item in data]

# 基本统计
stats = {
    "count": len(scores),
    "min": min(scores),
    "max": max(scores),
    "avg": sum(scores) / len(scores),
    "category_counts": dict(Counter(categories))
}

print(f"统计结果: {json.dumps(stats, indent=2)}")

# 分类统计
category_stats = {}
for category in ["A", "B", "C"]:
    cat_scores = [item["score"] for item in data if item["category"] == category]
    category_stats[category] = {
        "count": len(cat_scores),
        "avg": sum(cat_scores) / len(cat_scores) if cat_scores else 0,
        "min": min(cat_scores) if cat_scores else 0,
        "max": max(cat_scores) if cat_scores else 0
    }

print(f"分类统计: {json.dumps(category_stats, indent=2)}")

# 导出结果
with open('analysis_results.json', 'w') as f:
    json.dump({
        "overall_stats": stats,
        "category_stats": category_stats,
        "sample_data": data[:10]  # 前10条数据作为样本
    }, f, indent=2)

print("数据分析完成，结果已保存到 analysis_results.json")
"""
    
    result = client.execute_code(code, timeout=20)
    
    if result["success"]:
        print("✅ 数据分析成功!")
        print(f"输出:\n{result['stdout']}")
        print(f"执行时间: {result['execution_time']:.3f}秒")
        
        if "analysis_results.json" in result["files"]:
            content = base64.b64decode(result["files"]["analysis_results.json"]).decode('utf-8')
            analysis = json.loads(content)
            print(f"\n📊 分析结果预览:")
            print(f"总数: {analysis['overall_stats']['count']}")
            print(f"平均分: {analysis['overall_stats']['avg']:.2f}")
            print(f"分类分布: {analysis['overall_stats']['category_counts']}")
    else:
        print("❌ 数据分析失败!")
        print(f"错误: {result['error']}")


def main():
    """主函数"""
    print("SimplePySandbox 客户端示例")
    print("=" * 50)
    
    # 健康检查
    client = SandboxClient()
    health = client.health_check()
    
    if health.get("status") == "healthy":
        print("✅ 服务状态正常")
    else:
        print("❌ 服务不可用:", health.get("message", "未知错误"))
        return
    
    # 运行示例
    try:
        example_basic_execution()
        time.sleep(1)
        
        example_file_processing()
        time.sleep(1)
        
        example_data_analysis()
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n运行示例时出错: {e}")
    
    print("\n示例运行完成!")


if __name__ == "__main__":
    main()