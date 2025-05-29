import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """应用设置"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # 沙盒执行设置
    SANDBOX_TIMEOUT: int = 30
    MAX_TIMEOUT: int = 300
    MAX_CODE_LENGTH: int = 100000
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Docker设置
    DOCKER_IMAGE: str = "python:3.11-slim"
    WORK_DIR: str = "/sandbox"
    
    # 资源限制
    MEMORY_LIMIT: str = "512m"
    CPU_LIMIT: str = "1"
    
    # 网络设置
    NETWORK_MODE: str = "bridge"
    
    # 临时目录
    TEMP_DIR: str = "/tmp/sandbox"


# 创建全局设置实例
settings = Settings()
