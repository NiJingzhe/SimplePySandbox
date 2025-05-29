from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict
from enum import Enum


class PackageManager(str, Enum):
    """包管理器类型"""
    PIP = "pip"
    CONDA = "conda"
    APT = "apt"
    CUSTOM = "custom"


class EnvironmentScript(BaseModel):
    """环境配置脚本模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "data-science-env",
                "description": "数据科学环境，包含pandas、numpy、scikit-learn等",
                "base_image": "continuumio/miniconda3:latest",
                "setup_script": "#!/bin/bash\nset -e\nconda install -y numpy pandas scikit-learn\npip install matplotlib seaborn",
                "python_version": "3.11"
            }
        }
    )
    
    name: str = Field(..., description="环境名称", min_length=1, max_length=50)
    description: str = Field(default="", description="环境描述", max_length=200)
    base_image: str = Field(
        default="python:3.11-slim", 
        description="基础Docker镜像"
    )
    setup_script: str = Field(
        ..., 
        description="依赖安装脚本内容",
        min_length=1,
        max_length=10000
    )
    python_version: str = Field(
        default="3.11",
        description="Python版本"
    )
    
    @validator('name')
    def validate_name(cls, v):
        # 验证环境名称只包含字母数字和连字符
        import re
        if not re.match(r'^[a-zA-Z0-9-_]+$', v):
            raise ValueError('环境名称只能包含字母、数字、连字符和下划线')
        return v
    
    @validator('setup_script')
    def validate_setup_script(cls, v):
        # 基本的脚本安全性检查
        dangerous_commands = [
            'rm -rf /',
            'dd if=',
            'mkfs',
            ':(){ :|:& };:',  # fork bomb
            'curl | sh',
            'wget | sh'
        ]
        
        for dangerous in dangerous_commands:
            if dangerous in v:
                raise ValueError(f'脚本包含危险命令: {dangerous}')
        
        return v


class EnvironmentResponse(BaseModel):
    """环境响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "data-science-env",
                "description": "数据科学环境",
                "base_image": "continuumio/miniconda3:latest",
                "docker_image": "sandbox-data-science-env:latest",
                "status": "ready",
                "created_at": "2025-05-29T10:00:00Z",
                "last_used": "2025-05-29T12:30:00Z"
            }
        }
    )
    
    name: str = Field(..., description="环境名称")
    description: str = Field(..., description="环境描述")
    base_image: str = Field(..., description="基础Docker镜像")
    docker_image: str = Field(..., description="构建后的Docker镜像名称")
    status: str = Field(..., description="环境状态: building, ready, failed")
    created_at: str = Field(..., description="创建时间")
    last_used: Optional[str] = Field(default=None, description="最后使用时间")


class ExecuteWithEnvironmentRequest(BaseModel):
    """使用指定环境执行代码的请求模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "import pandas as pd\nprint(pd.__version__)",
                "environment": "data-science-env",
                "timeout": 30,
                "files": {}
            }
        }
    )
    
    code: str = Field(..., description="要执行的Python代码")
    environment: str = Field(..., description="要使用的环境名称")
    timeout: int = Field(default=30, ge=1, le=300, description="执行超时时间（秒）")
    files: Optional[Dict[str, str]] = Field(
        default=None,
        description="输入文件，键为文件名，值为base64编码的文件内容"
    )


class EnvironmentListResponse(BaseModel):
    """环境列表响应模型"""
    environments: List[EnvironmentResponse] = Field(..., description="环境列表")
    total: int = Field(..., description="环境总数")