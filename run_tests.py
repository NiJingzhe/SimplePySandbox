#!/usr/bin/env python3
"""
测试运行器
提供不同级别的测试运行选项
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type="all", verbose=False, coverage=False):
    """运行测试"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 基础pytest命令
    cmd = ["python", "-m", "pytest"]
    
    # 添加详细输出
    if verbose:
        cmd.append("-v")
    
    # 添加覆盖率
    if coverage:
        cmd.extend(["--cov=sandbox", "--cov=models", "--cov=config", "--cov-report=html"])
    
    # 根据测试类型添加路径和标记
    if test_type == "unit":
        cmd.extend(["-m", "unit", "tests/unit/"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration", "tests/integration/"])
    elif test_type == "system":
        cmd.extend(["-m", "system", "tests/system/"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance", "tests/performance/"])
    elif test_type == "quick":
        cmd.extend(["-m", "not slow", "tests/"])
    elif test_type == "slow":
        cmd.extend(["-m", "slow", "tests/"])
    elif test_type == "docker":
        cmd.extend(["-m", "requires_docker", "tests/"])
    else:  # all
        cmd.append("tests/")
    
    print(f"运行命令: {' '.join(cmd)}")
    return subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="SimplePySandbox测试运行器")
    parser.add_argument(
        "test_type", 
        choices=["all", "unit", "integration", "system", "performance", "quick", "slow", "docker"],
        default="all",
        nargs="?",
        help="测试类型"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-c", "--coverage", action="store_true", help="生成覆盖率报告")
    
    args = parser.parse_args()
    
    # 检查环境
    try:
        import pytest
    except ImportError:
        print("❌ pytest未安装，请运行: pip install pytest")
        sys.exit(1)
    
    if args.coverage:
        try:
            import pytest_cov
        except ImportError:
            print("❌ pytest-cov未安装，请运行: pip install pytest-cov")
            sys.exit(1)
    
    # 运行测试
    result = run_tests(args.test_type, args.verbose, args.coverage)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
