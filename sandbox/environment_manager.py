import os
import json
import asyncio
import subprocess
import shutil
import tempfile
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

from models.environment import EnvironmentScript, EnvironmentResponse
from config.settings import settings
from .utils import create_secure_temp_dir, cleanup_temp_dir


class EnvironmentManager:
    """环境管理器，负责创建和管理Conda虚拟环境"""
    
    def __init__(self):
        """初始化Conda环境管理器"""
        self._check_conda_installation()
        
        # 环境信息存储文件
        if os.path.exists("/app/data"):
            # Docker环境中的路径
            self.environments_file = "/app/data/environments.json"
            self.environments_dir = "/app/data/environments"
        else:
            # 本地环境中的路径
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data"
            self.environments_file = str(data_dir / "environments.json")
            self.environments_dir = str(data_dir / "environments")
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.environments_file), exist_ok=True)
        os.makedirs(self.environments_dir, exist_ok=True)
        
        # 加载现有环境信息
        self.environments = self._load_environments()
        
        # 获取conda信息
        self.conda_info = self._get_conda_info()
        print(f"✅ Conda连接成功: {self.conda_info['conda_version']}")
    
    def _check_conda_installation(self):
        """检查conda是否安装"""
        try:
            result = subprocess.run(
                ["conda", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("❌ 未找到conda安装，请确保conda已正确安装并在PATH中")
    
    def _get_conda_info(self) -> Dict:
        """获取conda信息"""
        try:
            result = subprocess.run(
                ["conda", "info", "--json"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            info = json.loads(result.stdout)
            return {
                "conda_version": info.get("conda_version"),
                "python_version": info.get("python_version"),
                "platform": info.get("platform"),
                "envs_dirs": info.get("envs_dirs", []),
                "root_prefix": info.get("root_prefix")
            }
        except Exception as e:
            raise RuntimeError(f"获取conda信息失败: {e}")
    
    def _load_environments(self) -> Dict[str, dict]:
        """加载环境信息"""
        try:
            if os.path.exists(self.environments_file):
                with open(self.environments_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载环境信息失败: {e}")
        return {}
    
    def _save_environments(self):
        """保存环境信息"""
        try:
            with open(self.environments_file, 'w', encoding='utf-8') as f:
                json.dump(self.environments, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存环境信息失败: {e}")
    
    async def create_environment(self, env_script: EnvironmentScript) -> EnvironmentResponse:
        """创建新的Conda环境"""
        if env_script.name in self.environments:
            raise ValueError(f"环境 '{env_script.name}' 已存在")
        
        # 生成conda环境名称
        conda_env_name = f"sandbox-{env_script.name}"
        
        # 记录环境信息
        env_info = {
            "name": env_script.name,
            "description": env_script.description,
            "base_image": env_script.base_image,  # 在conda中可以理解为base python版本
            "docker_image": None,  # Conda模式不使用Docker
            "conda_env_name": conda_env_name,
            "status": "building",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_used": None,
            "setup_script": env_script.setup_script,
            "python_version": env_script.python_version,
            "env_path": None  # 将在创建成功后填写
        }
        
        self.environments[env_script.name] = env_info
        self._save_environments()
        
        try:
            # 异步创建Conda环境
            await self._create_conda_environment(env_script, conda_env_name)
            
            # 获取环境路径
            env_path = await self._get_environment_path(conda_env_name)
            
            # 更新状态为就绪
            self.environments[env_script.name]["status"] = "ready"
            self.environments[env_script.name]["env_path"] = env_path
            self._save_environments()
            
            return EnvironmentResponse(**self.environments[env_script.name])
            
        except Exception as e:
            # 创建失败，更新状态
            self.environments[env_script.name]["status"] = "failed"
            self.environments[env_script.name]["error"] = str(e)
            self._save_environments()
            raise RuntimeError(f"环境创建失败: {str(e)}")
    
    async def _create_conda_environment(self, env_script: EnvironmentScript, conda_env_name: str):
        """创建Conda环境"""
        try:
            print(f"开始创建Conda环境: {conda_env_name}")
            
            # 确保conda环境目录存在并配置
            conda_envs_dir = os.path.join(os.path.dirname(self.environments_file), "conda_envs")
            os.makedirs(conda_envs_dir, exist_ok=True)
            
            # 配置conda使用自定义环境目录
            await self._run_conda_command([
                "conda", "config", "--add", "envs_dirs", conda_envs_dir
            ])
            
            # 步骤1: 创建基础环境，指定环境目录
            await self._run_conda_command([
                "conda", "create", "-p", os.path.join(conda_envs_dir, conda_env_name),
                f"python={env_script.python_version}", 
                "-y"
            ])
            
            # 步骤2: 解析并执行安装脚本
            await self._execute_setup_script(conda_env_name, env_script.setup_script, conda_envs_dir)
            
            print(f"Conda环境创建完成: {conda_env_name}")
            
        except Exception as e:
            # 创建失败时清理环境
            try:
                conda_envs_dir = os.path.join(os.path.dirname(self.environments_file), "conda_envs")
                env_path = os.path.join(conda_envs_dir, conda_env_name)
                if os.path.exists(env_path):
                    await self._run_conda_command(["conda", "env", "remove", "-p", env_path, "-y"])
            except:
                pass
            raise e
    
    async def _execute_setup_script(self, conda_env_name: str, setup_script: str, conda_envs_dir: Optional[str] = None):
        """执行环境安装脚本"""
        temp_script = None
        try:
            # 创建临时脚本文件
            temp_script = tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.sh', 
                delete=False,
                encoding='utf-8'
            )
            
            # 确定环境路径
            if conda_envs_dir:
                env_path = os.path.join(conda_envs_dir, conda_env_name)
                activate_cmd = f'conda activate "{env_path}"'
            else:
                activate_cmd = f'conda activate {conda_env_name}'
            
            # 写入脚本内容，添加conda环境激活
            script_content = f"""#!/bin/bash
set -e

# 激活conda环境
source "$(conda info --base)/etc/profile.d/conda.sh"
{activate_cmd}

echo "开始在环境 {conda_env_name} 中安装依赖..."

# 执行用户脚本
{setup_script}

echo "依赖安装完成!"

# 确保脚本正常退出
exit 0
"""
            temp_script.write(script_content)
            temp_script.close()
            
            # 设置执行权限
            os.chmod(temp_script.name, 0o755)
            
            # 执行脚本
            await self._run_bash_script(temp_script.name)
            
        finally:
            # 清理临时文件
            if temp_script and os.path.exists(temp_script.name):
                os.unlink(temp_script.name)
    
    async def _run_conda_command(self, cmd: List[str]):
        """异步运行conda命令"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._run_command_sync, cmd)
        return result
    
    async def _run_bash_script(self, script_path: str):
        """异步运行bash脚本"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._run_command_sync, ["bash", script_path])
        return result
    
    def _run_command_sync(self, cmd: List[str]):
        """同步运行命令"""
        try:
            print(f"执行命令: {' '.join(cmd)}")
            
            # 使用Popen以便更好地控制进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )
            
            try:
                stdout, stderr = process.communicate(timeout=600)  # 10分钟超时
                
                if stdout:
                    print(f"输出: {stdout}")
                if stderr:
                    print(f"错误输出: {stderr}")
                
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, cmd, stdout, stderr)
                
                # 创建模拟的结果对象
                class Result:
                    def __init__(self, returncode, stdout, stderr):
                        self.returncode = returncode
                        self.stdout = stdout
                        self.stderr = stderr
                
                return Result(process.returncode, stdout, stderr)
                
            except subprocess.TimeoutExpired:
                # 超时时杀死进程
                process.kill()
                process.wait()
                raise subprocess.TimeoutExpired(cmd, 600)
            finally:
                # 确保进程被清理
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
            
        except subprocess.CalledProcessError as e:
            error_msg = f"命令执行失败: {' '.join(cmd)}\n"
            error_msg += f"返回码: {e.returncode}\n"
            error_msg += f"标准输出: {e.stdout}\n"
            error_msg += f"错误输出: {e.stderr}"
            raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"命令执行超时: {' '.join(cmd)}")
    
    async def _get_environment_path(self, conda_env_name: str) -> str:
        """获取conda环境路径"""
        try:
            # 首先尝试查找自定义路径中的环境
            conda_envs_dir = os.path.join(os.path.dirname(self.environments_file), "conda_envs")
            custom_env_path = os.path.join(conda_envs_dir, conda_env_name)
            
            if os.path.exists(custom_env_path):
                return custom_env_path
            
            # 如果自定义路径中没有，则查询conda的环境列表
            result = await self._run_conda_command([
                "conda", "info", "--envs", "--json"
            ])
            
            envs_info = json.loads(result.stdout)
            envs = envs_info.get("envs", [])
            
            for env_path in envs:
                if env_path.endswith(conda_env_name):
                    return env_path
            
            raise RuntimeError(f"未找到环境 {conda_env_name} 的路径")
            
        except Exception as e:
            raise RuntimeError(f"获取环境路径失败: {e}")
    
    def get_environment(self, name: str) -> Optional[EnvironmentResponse]:
        """获取指定环境信息"""
        if name in self.environments:
            return EnvironmentResponse(**self.environments[name])
        return None
    
    def list_environments(self) -> List[EnvironmentResponse]:
        """列出所有环境"""
        return [EnvironmentResponse(**env_info) for env_info in self.environments.values()]
    
    async def delete_environment(self, name: str) -> bool:
        """删除环境"""
        if name not in self.environments:
            return False
        
        try:
            # 删除Conda环境
            conda_env_name = self.environments[name]["conda_env_name"]
            try:
                await self._run_conda_command([
                    "conda", "env", "remove", "-n", conda_env_name, "-y"
                ])
                print(f"已删除Conda环境: {conda_env_name}")
            except Exception as e:
                print(f"删除Conda环境失败: {e}")
            
            # 从记录中移除
            del self.environments[name]
            self._save_environments()
            
            return True
            
        except Exception as e:
            print(f"删除环境失败: {e}")
            return False
    
    def update_last_used(self, name: str):
        """更新环境最后使用时间"""
        if name in self.environments:
            self.environments[name]["last_used"] = datetime.now(timezone.utc).isoformat()
            self._save_environments()
    
    def get_environment_info(self, name: str) -> Optional[Dict]:
        """获取环境的详细信息"""
        if name in self.environments and self.environments[name]["status"] == "ready":
            env_info = self.environments[name].copy()
            # 添加Python可执行文件路径
            if "env_path" in env_info and env_info["env_path"]:
                if sys.platform == "win32":
                    python_exe = os.path.join(env_info["env_path"], "python.exe")
                else:
                    python_exe = os.path.join(env_info["env_path"], "bin", "python")
                env_info["python_executable"] = python_exe
            return env_info
        return None


# 全局环境管理器实例
environment_manager = EnvironmentManager()
