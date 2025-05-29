import docker
import asyncio
import tempfile
import os
import base64
import time
import shutil
from typing import Dict, Optional
from pathlib import Path

from models.request import ExecuteResponse
from config.settings import settings
from .utils import create_secure_temp_dir, cleanup_temp_dir, validate_filename


class CodeExecutor:
    """代码执行器，负责在Docker容器中安全执行Python代码"""
    
    def __init__(self):
        """初始化Docker客户端"""
        try:
            self.docker_client = docker.from_env()
            # 测试Docker连接
            self.docker_client.ping()
            print("✅ Docker连接成功")
        except Exception as e:
            print(f"❌ Docker连接失败: {e}")
            raise RuntimeError(f"无法连接到Docker: {e}")
    
    async def execute(
        self, 
        code: str, 
        timeout: int = 30, 
        input_files: Optional[Dict[str, str]] = None,
        environment: Optional[str] = None
    ) -> ExecuteResponse:
        """
        执行Python代码
        
        Args:
            code: 要执行的Python代码
            timeout: 执行超时时间（秒）
            input_files: 输入文件字典，键为文件名，值为base64编码的内容
            environment: 要使用的环境名称，如果为None则使用默认环境
            
        Returns:
            ExecuteResponse: 执行结果
        """
        start_time = time.time()
        temp_dir = None
        
        try:
            # 创建临时工作目录
            temp_dir = create_secure_temp_dir()
            
            # 准备输入文件
            if input_files:
                await self._prepare_input_files(temp_dir, input_files)
            
            # 创建代码文件
            code_file = os.path.join(temp_dir, "main.py")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # 在Docker容器中执行代码
            result = await self._run_in_container(temp_dir, timeout, environment)
            
            # 收集输出文件
            output_files = await self._collect_output_files(temp_dir)
            
            execution_time = time.time() - start_time
            
            return ExecuteResponse(
                success=result["success"],
                stdout=result["stdout"],
                stderr=result["stderr"],
                execution_time=execution_time,
                files=output_files,
                error=result.get("error")
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecuteResponse(
                success=False,
                stdout="",
                stderr="",
                execution_time=execution_time,
                files={},
                error=f"执行错误: {str(e)}"
            )
        finally:
            # 清理临时目录
            if temp_dir:
                cleanup_temp_dir(temp_dir)
    
    async def _prepare_input_files(self, temp_dir: str, input_files: Dict[str, str]):
        """准备输入文件"""
        for filename, content_b64 in input_files.items():
            # 验证文件名安全性
            if not validate_filename(filename):
                raise ValueError(f"不安全的文件名: {filename}")
            
            try:
                # 解码base64内容
                content = base64.b64decode(content_b64)
                
                # 检查文件大小
                if len(content) > settings.MAX_FILE_SIZE:
                    raise ValueError(f"文件 {filename} 超过大小限制")
                
                # 写入文件
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(content)
                    
            except Exception as e:
                raise ValueError(f"处理文件 {filename} 时出错: {str(e)}")
    
    async def _run_in_container(self, temp_dir: str, timeout: int, environment: Optional[str] = None) -> Dict:
        """在Docker容器中运行代码"""
        try:
            # 确定要使用的Docker镜像
            docker_image = settings.DOCKER_IMAGE
            if environment:
                from .environment_manager import environment_manager
                custom_image = environment_manager.get_environment_image(environment)
                if custom_image:
                    docker_image = custom_image
                    # 更新最后使用时间
                    environment_manager.update_last_used(environment)
                else:
                    raise ValueError(f"环境 '{environment}' 不存在或未就绪")
            
            # 容器配置
            container_config = {
                "image": docker_image,
                "command": ["python", "/sandbox/main.py"],
                "working_dir": "/sandbox",
                "volumes": {temp_dir: {"bind": "/sandbox", "mode": "rw"}},
                "mem_limit": settings.MEMORY_LIMIT,
                "cpu_quota": int(float(settings.CPU_LIMIT) * 100000),
                "cpu_period": 100000,
                "network_mode": settings.NETWORK_MODE,
            }
            
            # 运行容器
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._run_container_sync, 
                container_config, 
                timeout
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "error": f"容器执行错误: {str(e)}"
            }
    
    def _run_container_sync(self, config: Dict, timeout: int) -> Dict:
        """同步方式运行容器 - 使用简化的方法避免SDK问题"""
        import subprocess
        import json
        
        try:
            # 获取volume mapping
            volumes = config.get("volumes", {})
            volume_mount = ""
            if volumes:
                # volumes格式: {temp_dir: {"bind": "/sandbox", "mode": "rw"}}
                for host_path, container_config in volumes.items():
                    container_path = container_config.get("bind", "/sandbox")
                    # 将容器内路径转换为宿主机路径
                    # /app/data/temp/sandbox_xxx -> /tmp/sandbox-exec/sandbox_xxx
                    if host_path.startswith("/app/data/temp/"):
                        host_path = host_path.replace("/app/data/temp/", "/tmp/sandbox-exec/")
                    volume_mount = f"{host_path}:{container_path}"
                    break
            
            # 构建docker run命令
            cmd = [
                "docker", "run", "--rm",
                "--memory", config.get("mem_limit", "512m"),
                "--cpus", str(float(config.get("cpu_quota", 100000)) / 100000),
                "--network", config.get("network_mode", "bridge")
            ]
            
            if volume_mount:
                cmd.extend(["-v", volume_mount])
                
            cmd.extend([
                "-w", config.get("working_dir", "/sandbox"),
                config["image"]
            ] + config["command"])
            
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            else:
                return {
                    "success": False,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "error": f"代码执行失败，退出码: {result.returncode}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "error": f"代码执行超时（{timeout}秒）"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "error": f"容器运行错误: {str(e)}"
            }
    
    async def _collect_output_files(self, temp_dir: str) -> Dict[str, str]:
        """收集输出文件并转换为base64"""
        output_files = {}
        
        try:
            for item in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, item)
                
                # 跳过代码文件和目录
                if item == "main.py" or os.path.isdir(file_path):
                    continue
                
                # 检查文件大小
                if os.path.getsize(file_path) > settings.MAX_FILE_SIZE:
                    continue
                
                # 读取文件并编码为base64
                with open(file_path, "rb") as f:
                    content = f.read()
                    content_b64 = base64.b64encode(content).decode('utf-8')
                    output_files[item] = content_b64
                    
        except Exception as e:
            print(f"收集输出文件时出错: {e}")
        
        return output_files
