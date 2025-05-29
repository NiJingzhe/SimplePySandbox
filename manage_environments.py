#!/usr/bin/env python3
# filepath: /Users/lildino/Project/SimplePySandbox/manage_environments.py
"""
环境管理CLI工具
用于快速创建和管理沙盒环境
"""

import requests
import json
import time
import argparse
import sys
from pathlib import Path


class EnvironmentManager:
    """环境管理器客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def create_environment(self, name: str, script_file: str, description: str = "", 
                         python_version: str = "3.11"):
        """创建环境"""
        
        # 读取脚本文件
        script_path = Path(script_file)
        if not script_path.exists():
            print(f"❌ 脚本文件不存在: {script_file}")
            return False
        
        with open(script_path, 'r', encoding='utf-8') as f:
            setup_script = f.read()
        
        env_config = {
            "name": name,
            "description": description,
            "setup_script": setup_script,
            "python_version": python_version
        }
        
        print(f"🔧 创建环境 '{name}'...")
        print(f"📄 脚本文件: {script_file}")
        print(f"🐍 Python版本: {python_version}")
        
        try:
            response = requests.post(f"{self.base_url}/environments", json=env_config)
            
            if response.status_code == 200:
                env_info = response.json()
                print(f"✅ 环境创建成功!")
                print(f"   名称: {env_info['name']}")
                print(f"   状态: {env_info['status']}")
                print(f"   Python版本: {env_info.get('python_version', '未知')}")
                return True
            else:
                print(f"❌ 环境创建失败: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def list_environments(self):
        """列出所有环境"""
        
        print("📋 环境列表:")
        
        try:
            response = requests.get(f"{self.base_url}/environments")
            
            if response.status_code == 200:
                env_list = response.json()
                if env_list["total"] == 0:
                    print("   (暂无环境)")
                    return True
                
                print(f"   共 {env_list['total']} 个环境:")
                print()
                
                for env in env_list["environments"]:
                    status_icon = {
                        "ready": "✅",
                        "building": "🔧",
                        "failed": "❌"
                    }.get(env["status"], "❓")
                    
                    print(f"   {status_icon} {env['name']}")
                    print(f"      状态: {env['status']}")
                    print(f"      描述: {env['description']}")
                    print(f"      Python版本: {env.get('python_version', '未知')}")
                    print(f"      创建时间: {env['created_at']}")
                    if env.get('last_used'):
                        print(f"      最后使用: {env['last_used']}")
                    print()
                
                return True
            else:
                print(f"❌ 获取环境列表失败: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def get_environment(self, name: str):
        """获取环境详情"""
        
        print(f"🔍 环境详情: {name}")
        
        try:
            response = requests.get(f"{self.base_url}/environments/{name}")
            
            if response.status_code == 200:
                env = response.json()
                
                status_icon = {
                    "ready": "✅",
                    "building": "🔧", 
                    "failed": "❌"
                }.get(env["status"], "❓")
                
                print(f"   {status_icon} 名称: {env['name']}")
                print(f"   📝 描述: {env['description']}")
                print(f"   🐍 Python版本: {env.get('python_version', '未知')}")
                print(f"   📊 状态: {env['status']}")
                print(f"   📅 创建时间: {env['created_at']}")
                if env.get('last_used'):
                    print(f"   🕐 最后使用: {env['last_used']}")
                
                return True
            elif response.status_code == 404:
                print(f"❌ 环境 '{name}' 不存在")
                return False
            else:
                print(f"❌ 获取环境详情失败: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def delete_environment(self, name: str):
        """删除环境"""
        
        print(f"🗑️  删除环境 '{name}'...")
        
        # 确认删除
        confirm = input(f"确定要删除环境 '{name}' 吗? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("取消删除")
            return False
        
        try:
            response = requests.delete(f"{self.base_url}/environments/{name}")
            
            if response.status_code == 200:
                print(f"✅ 环境 '{name}' 已删除")
                return True
            elif response.status_code == 404:
                print(f"❌ 环境 '{name}' 不存在")
                return False
            else:
                print(f"❌ 删除环境失败: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def wait_for_environment(self, name: str, max_minutes: int = 10):
        """等待环境构建完成"""
        
        print(f"⏳ 等待环境 '{name}' 构建完成...")
        
        max_retries = max_minutes * 6  # 每10秒检查一次
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(f"{self.base_url}/environments/{name}")
                
                if response.status_code == 200:
                    env_info = response.json()
                    status = env_info["status"]
                    
                    if status == "ready":
                        print("✅ 环境构建完成!")
                        return True
                    elif status == "failed":
                        print(f"❌ 环境构建失败")
                        return False
                    else:
                        elapsed = (retry_count + 1) * 10
                        print(f"⏳ 构建中... ({elapsed}s/{max_minutes * 60}s)")
                        time.sleep(10)
                        retry_count += 1
                else:
                    print(f"❌ 检查环境状态失败: {response.text}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ 请求失败: {e}")
                return False
        
        print("❌ 环境构建超时")
        return False


def main():
    """主函数"""
    
    parser = argparse.ArgumentParser(description="SimplePySandbox 环境管理工具")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 创建环境
    create_parser = subparsers.add_parser("create", help="创建新环境")
    create_parser.add_argument("name", help="环境名称")
    create_parser.add_argument("script", help="环境配置脚本文件路径")
    create_parser.add_argument("--description", default="", help="环境描述")
    create_parser.add_argument("--python-version", default="3.11", help="Python版本")
    create_parser.add_argument("--wait", action="store_true", help="等待环境构建完成")
    create_parser.add_argument("--wait-timeout", type=int, default=10, help="等待超时时间（分钟）")
    
    # 列出环境
    list_parser = subparsers.add_parser("list", help="列出所有环境")
    
    # 查看环境详情
    info_parser = subparsers.add_parser("info", help="查看环境详情")
    info_parser.add_argument("name", help="环境名称")
    
    # 删除环境
    delete_parser = subparsers.add_parser("delete", help="删除环境")
    delete_parser.add_argument("name", help="环境名称")
    
    # 等待环境构建
    wait_parser = subparsers.add_parser("wait", help="等待环境构建完成")
    wait_parser.add_argument("name", help="环境名称")
    wait_parser.add_argument("--timeout", type=int, default=10, help="等待超时时间（分钟）")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = EnvironmentManager(args.url)
    
    success = False
    
    if args.command == "create":
        success = manager.create_environment(
            args.name, 
            args.script, 
            args.description, 
            args.python_version
        )
        
        if success and args.wait:
            success = manager.wait_for_environment(args.name, args.wait_timeout)
    
    elif args.command == "list":
        success = manager.list_environments()
    
    elif args.command == "info":
        success = manager.get_environment(args.name)
    
    elif args.command == "delete":
        success = manager.delete_environment(args.name)
    
    elif args.command == "wait":
        success = manager.wait_for_environment(args.name, args.timeout)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
