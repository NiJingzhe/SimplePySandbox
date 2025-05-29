from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict
from datetime import datetime


class ExecuteRequest(BaseModel):
    """代码执行请求模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "print('Hello, World!')",
                "timeout": 30,
                "files": {
                    "input.txt": "SGVsbG8gV29ybGQ="
                },
                "environment": "default"
            }
        }
    )
    
    code: str = Field(..., description="要执行的Python代码")
    timeout: int = Field(default=30, ge=1, le=300, description="执行超时时间（秒）")
    files: Optional[Dict[str, str]] = Field(
        default=None, 
        description="输入文件，键为文件名，值为base64编码的文件内容"
    )
    environment: Optional[str] = Field(
        default=None,
        description="要使用的环境名称，如果为None则使用默认环境"
    )


class ExecuteResponse(BaseModel):
    """代码执行响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "stdout": "Hello, World!\n",
                "stderr": "",
                "execution_time": 0.123,
                "files": {
                    "output.txt": "T3V0cHV0IGRhdGE="
                },
                "error": None
            }
        }
    )
    
    success: bool = Field(..., description="执行是否成功")
    stdout: str = Field(..., description="标准输出")
    stderr: str = Field(..., description="标准错误输出")
    execution_time: float = Field(..., description="执行时间（秒）")
    files: Dict[str, str] = Field(..., description="生成的文件，值为base64编码")
    error: Optional[str] = Field(default=None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2025-05-29T10:00:00Z"
            }
        }
    )
    
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
