import asyncio
import subprocess
import os
import base64
import time
import sys
import signal
from typing import Dict, Optional
from pathlib import Path

from models.request import ExecuteResponse
from config.settings import settings
from .utils import create_secure_temp_dir, cleanup_temp_dir, validate_filename


class CodeExecutor:
    """Conda代码执行器，负责在Conda虚拟环境中安全执行Python代码"""
    
    def __init__(self):
        """初始化Conda执行器"""
        self._check_conda_available()
        print("✅ Conda执行器初始化成功")
    
    def _check_conda_available(self):
        """检查conda是否可用"""
        try:
            subprocess.run(
                ["conda", "--version"], 
                capture_output=True, 
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Conda不可用，请确保已正确安装conda")
    
    async def execute(
        self, 
        code: str, 
        timeout: int = 30, 
        input_files: Optional[Dict[str, str]] = None,
        environment: Optional[str] = None
    ) -> ExecuteResponse:
        """
        在Conda环境中执行Python代码
        
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
            
            # 在Conda环境中执行代码
            result = await self._run_in_conda_env(temp_dir, timeout, environment)
            
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
    
    async def _run_in_conda_env(self, temp_dir: str, timeout: int, environment: Optional[str] = None) -> Dict:
        """在Conda环境中运行代码"""
        try:
            # 确定要使用的Python可执行文件
            python_executable = sys.executable  # 默认使用当前Python
            
            if environment:
                from .environment_manager import environment_manager
                env_info = environment_manager.get_environment_info(environment)
                if env_info and "python_executable" in env_info:
                    python_executable = env_info["python_executable"]
                    # 更新最后使用时间
                    environment_manager.update_last_used(environment)
                else:
                    raise ValueError(f"环境 '{environment}' 不存在或未就绪")
            
            # 构建执行命令
            cmd = [python_executable, "main.py"]
            
            # 运行代码
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._run_python_sync, 
                cmd,
                temp_dir,
                timeout
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "error": f"环境执行错误: {str(e)}"
            }
    
    def _run_python_sync(self, cmd: list, work_dir: str, timeout: int) -> Dict:
        """同步方式运行Python代码"""
        try:
            # 设置环境变量
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONPATH"] = work_dir
            
            # 在某些系统上设置资源限制
            def preexec_fn():
                try:
                    # 设置进程组，便于终止
                    if hasattr(os, 'setpgrp'):
                        os.setpgrp()
                    
                    # 在Unix系统上设置资源限制
                    if hasattr(os, 'setrlimit'):
                        import resource
                        
                        # 限制CPU时间 (秒)
                        if hasattr(resource, 'RLIMIT_CPU'):
                            resource.setrlimit(resource.RLIMIT_CPU, (timeout + 5, timeout + 10))
                        
                        # 限制内存使用 (字节) - 默认512MB
                        if hasattr(resource, 'RLIMIT_AS'):
                            memory_limit = self._parse_memory_limit("512m")
                            if memory_limit > 0:
                                resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
                        
                        # 限制文件大小 - 默认10MB
                        if hasattr(resource, 'RLIMIT_FSIZE'):
                            max_file_size = 10 * 1024 * 1024  # 10MB
                            resource.setrlimit(resource.RLIMIT_FSIZE, (max_file_size, max_file_size))
                except Exception:
                    # 如果设置失败，继续执行但不设置限制
                    pass
            
            # 在Windows上不能使用preexec_fn
            if sys.platform == "win32":
                preexec_fn = None
            
            # 为了调试，暂时禁用preexec_fn
            preexec_fn = None # type: ignore
            
            # 执行命令（暂时不使用preexec_fn进行调试）
            popen_kwargs = {
                "cwd": work_dir,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "env": env,
                "text": True,
            }
            
            # 在非Windows系统上可以使用preexec_fn（暂时禁用用于调试）
            # if sys.platform != "win32" and preexec_fn:
            #     popen_kwargs["preexec_fn"] = preexec_fn
            
            process = subprocess.Popen(cmd, **popen_kwargs)
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "stdout": stdout,
                        "stderr": stderr,
                    }
                else:
                    return {
                        "success": False,
                        "stdout": stdout,
                        "stderr": stderr,
                        "error": f"代码执行失败，退出码: {process.returncode}"
                    }
                    
            except subprocess.TimeoutExpired:
                # 超时处理
                self._terminate_process(process)
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
                "error": f"执行错误: {str(e)}"
            }
    
    def _terminate_process(self, process):
        """终止进程及其子进程"""
        try:
            if sys.platform == "win32":
                # Windows
                process.terminate()
            else:
                # Unix-like systems
                try:
                    # 尝试优雅地终止进程组
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=2)
                except (subprocess.TimeoutExpired, ProcessLookupError):
                    # 强制终止
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        except Exception as e:
            print(f"终止进程时出错: {e}")
    
    def _parse_memory_limit(self, memory_str: str) -> int:
        """解析内存限制字符串，返回字节数"""
        try:
            if memory_str.endswith('m') or memory_str.endswith('M'):
                return int(memory_str[:-1]) * 1024 * 1024
            elif memory_str.endswith('g') or memory_str.endswith('G'):
                return int(memory_str[:-1]) * 1024 * 1024 * 1024
            else:
                return int(memory_str)
        except:
            return 512 * 1024 * 1024  # 默认512MB
    
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


# 全局代码执行器实例
code_executor = CodeExecutor()
