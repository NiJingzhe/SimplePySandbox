import docker
import os
import tempfile
import time
import json
import asyncio
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

from models.environment import EnvironmentScript, EnvironmentResponse
from config.settings import settings
from .utils import create_secure_temp_dir, cleanup_temp_dir


class EnvironmentManager:
    """环境管理器，负责创建和管理自定义执行环境"""
    
    def __init__(self):
        """初始化环境管理器"""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            print("✅ Docker连接成功")
        except Exception as e:
            print(f"❌ Docker连接失败: {e}")
            raise RuntimeError(f"无法连接到Docker: {e}")
        
        # 环境信息存储文件 - 根据环境选择不同路径
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
        """创建新的执行环境"""
        if env_script.name in self.environments:
            raise ValueError(f"环境 '{env_script.name}' 已存在")
        
        # 生成Docker镜像名称
        docker_image = f"sandbox-{env_script.name}:latest"
        
        # 记录环境信息
        env_info = {
            "name": env_script.name,
            "description": env_script.description,
            "base_image": env_script.base_image,
            "docker_image": docker_image,
            "status": "building",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_used": None,
            "setup_script": env_script.setup_script,
            "python_version": env_script.python_version
        }
        
        self.environments[env_script.name] = env_info
        self._save_environments()
        
        try:
            # 异步构建Docker镜像
            await self._build_environment_image(env_script, docker_image)
            
            # 更新状态为就绪
            self.environments[env_script.name]["status"] = "ready"
            self._save_environments()
            
            return EnvironmentResponse(**self.environments[env_script.name])
            
        except Exception as e:
            # 构建失败，更新状态
            self.environments[env_script.name]["status"] = "failed"
            self.environments[env_script.name]["error"] = str(e)
            self._save_environments()
            raise RuntimeError(f"环境构建失败: {str(e)}")
    
    async def _build_environment_image(self, env_script: EnvironmentScript, docker_image: str):
        """构建环境Docker镜像"""
        temp_dir = None
        try:
            # 创建临时构建目录
            temp_dir = create_secure_temp_dir()
            
            # 准备构建文件
            await self._prepare_build_files(temp_dir, env_script)
            
            # 构建Docker镜像
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._build_image_sync,
                temp_dir,
                docker_image
            )
            
        finally:
            if temp_dir:
                cleanup_temp_dir(temp_dir)
    
    async def _prepare_build_files(self, build_dir: str, env_script: EnvironmentScript):
        """准备构建所需的文件"""
        # 创建安装脚本
        setup_script_path = os.path.join(build_dir, "setup_env.sh")
        with open(setup_script_path, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n")
            f.write("set -e\n")
            f.write("echo '开始安装环境依赖...'\n\n")
            f.write(env_script.setup_script)
            f.write("\n\necho '环境依赖安装完成!'\n")
        
        # 设置执行权限
        os.chmod(setup_script_path, 0o755)
        
        # 创建Dockerfile
        dockerfile_content = self._generate_dockerfile(env_script)
        dockerfile_path = os.path.join(build_dir, "Dockerfile")
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
    
    def _generate_dockerfile(self, env_script: EnvironmentScript) -> str:
        """生成Dockerfile内容"""
        
        # 检查是否使用conda基础镜像
        is_conda_image = "conda" in env_script.base_image.lower() or "miniconda" in env_script.base_image.lower()
        
        dockerfile = f"""# 自动生成的环境Dockerfile
FROM {env_script.base_image}

# 设置工作目录
WORKDIR /sandbox

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

"""
        
        if not is_conda_image:
            # 对于非conda镜像，安装基础系统依赖
            dockerfile += """# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    git \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

"""
        else:
            # 对于conda镜像，确保conda和pip可用
            dockerfile += """# 更新conda和pip
RUN conda update -n base -c defaults conda && \\
    conda install -y pip

"""
        
        dockerfile += """# 复制安装脚本
COPY setup_env.sh /tmp/setup_env.sh

# 执行环境配置脚本
RUN chmod +x /tmp/setup_env.sh && \\
    /tmp/setup_env.sh && \\
    rm /tmp/setup_env.sh

# 创建非root用户
RUN useradd -m -u 1000 sandbox && \\
    chown -R sandbox:sandbox /sandbox

# 切换到非root用户
USER sandbox

# 设置默认命令
CMD ["python"]
"""
        
        return dockerfile
    
    def _build_image_sync(self, build_dir: str, docker_image: str):
        """同步构建Docker镜像"""
        try:
            print(f"开始构建镜像: {docker_image}")
            
            # 构建镜像
            image, build_logs = self.docker_client.images.build(
                path=build_dir,
                tag=docker_image,
                rm=True,
                forcerm=True
            )
            
            # 输出构建日志
            for log in build_logs:
                if 'stream' in log:  # type: ignore
                    print(log['stream'].strip())  # type: ignore
            
            print(f"镜像构建完成: {docker_image}")
            
        except Exception as e:
            print(f"镜像构建失败: {e}")
            raise e
    
    def get_environment(self, name: str) -> Optional[EnvironmentResponse]:
        """获取指定环境信息"""
        if name in self.environments:
            return EnvironmentResponse(**self.environments[name])
        return None
    
    def list_environments(self) -> List[EnvironmentResponse]:
        """列出所有环境"""
        return [EnvironmentResponse(**env_info) for env_info in self.environments.values()]
    
    def delete_environment(self, name: str) -> bool:
        """删除环境"""
        if name not in self.environments:
            return False
        
        try:
            # 删除Docker镜像
            docker_image = self.environments[name]["docker_image"]
            try:
                self.docker_client.images.remove(docker_image, force=True)
                print(f"已删除Docker镜像: {docker_image}")
            except docker.errors.ImageNotFound:  # type: ignore
                print(f"Docker镜像不存在: {docker_image}")
            
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
    
    def get_environment_image(self, name: str) -> Optional[str]:
        """获取环境的Docker镜像名称"""
        if name in self.environments and self.environments[name]["status"] == "ready":
            return self.environments[name]["docker_image"]
        return None


# 全局环境管理器实例
environment_manager = EnvironmentManager()
