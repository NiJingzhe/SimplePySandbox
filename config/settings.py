import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class ExecutionMode(str, Enum):
    """执行模式枚举"""
    CONDA = "conda"


class Settings(BaseSettings):
    """应用设置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # 执行模式设置
    EXECUTION_MODE: ExecutionMode = ExecutionMode.CONDA
    
    # 沙盒执行设置
    SANDBOX_TIMEOUT: int = 30
    MAX_TIMEOUT: int = 300
    MAX_CODE_LENGTH: int = 100000
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Conda环境设置
    CONDA_BASE_PATH: str = os.path.expanduser("~/miniconda3")
    CONDA_ENVS_PATH: str = os.path.expanduser("~/miniconda3/envs")
    
    # 临时目录
    TEMP_DIR: str = "/tmp/sandbox"


# 创建全局设置实例
settings = Settings()
