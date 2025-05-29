from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timezone

from models.request import ExecuteRequest, ExecuteResponse, HealthResponse
from models.environment import (
    EnvironmentScript, EnvironmentResponse, EnvironmentListResponse,
    ExecuteWithEnvironmentRequest
)
from sandbox.executor import CodeExecutor
from sandbox.environment_manager import environment_manager
from config.settings import settings

# 初始化执行器和环境管理器
executor = CodeExecutor()
env_manager = environment_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 SimplePySandbox 启动中...")
    yield
    # 关闭时清理
    print("🛑 SimplePySandbox 正在关闭...")


app = FastAPI(
    title="SimplePySandbox",
    description="一个安全的Python代码执行沙盒",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/", tags=["Root"])
async def root():
    """根路径，返回API信息"""
    return {
        "message": "SimplePySandbox API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc)
    )


@app.post("/execute", response_model=ExecuteResponse, tags=["Execution"])
async def execute_code(request: ExecuteRequest):
    """
    执行Python代码
    
    Args:
        request: 包含代码、超时设置和输入文件的请求
        
    Returns:
        ExecuteResponse: 执行结果，包括输出、错误和生成的文件
    """
    try:
        # 验证请求
        if len(request.code.strip()) == 0:
            raise HTTPException(status_code=400, detail="代码不能为空")
        
        if len(request.code) > settings.MAX_CODE_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"代码长度不能超过 {settings.MAX_CODE_LENGTH} 字符"
            )
        
        if request.timeout > settings.MAX_TIMEOUT:
            raise HTTPException(
                status_code=400,
                detail=f"超时时间不能超过 {settings.MAX_TIMEOUT} 秒"
            )
        
        # 执行代码
        result = await executor.execute(
            code=request.code,
            timeout=request.timeout,
            input_files=request.files or {},
            environment=request.environment
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return ExecuteResponse(
            success=False,
            stdout="",
            stderr="",
            execution_time=0.0,
            files={},
            error=f"执行出错: {str(e)}"
        )


# 环境管理端点

@app.post("/environments", response_model=EnvironmentResponse, tags=["环境管理"])
async def create_environment(env_script: EnvironmentScript):
    """
    创建新的执行环境
    
    Args:
        env_script: 环境配置脚本
        
    Returns:
        EnvironmentResponse: 创建的环境信息
    """
    try:
        result = await env_manager.create_environment(env_script)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建环境失败: {str(e)}")


@app.get("/environments", response_model=EnvironmentListResponse, tags=["环境管理"])
async def list_environments():
    """
    列出所有环境
    
    Returns:
        EnvironmentListResponse: 环境列表
    """
    try:
        environments = env_manager.list_environments()
        return EnvironmentListResponse(
            environments=environments,
            total=len(environments)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取环境列表失败: {str(e)}")


@app.get("/environments/{environment_name}", response_model=EnvironmentResponse, tags=["环境管理"])
async def get_environment(environment_name: str):
    """
    获取指定环境信息
    
    Args:
        environment_name: 环境名称
        
    Returns:
        EnvironmentResponse: 环境信息
    """
    try:
        env = env_manager.get_environment(environment_name)
        if not env:
            raise HTTPException(status_code=404, detail=f"环境 '{environment_name}' 不存在")
        return env
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取环境信息失败: {str(e)}")


@app.delete("/environments/{environment_name}", tags=["环境管理"])
async def delete_environment(environment_name: str):
    """
    删除指定环境
    
    Args:
        environment_name: 环境名称
        
    Returns:
        dict: 删除结果
    """
    try:
        success = await env_manager.delete_environment(environment_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"环境 '{environment_name}' 不存在")
        return {"message": f"环境 '{environment_name}' 已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除环境失败: {str(e)}")


@app.post("/execute-with-environment", response_model=ExecuteResponse, tags=["代码执行"])
async def execute_with_environment(request: ExecuteWithEnvironmentRequest):
    """
    使用指定环境执行Python代码
    
    Args:
        request: 包含代码、环境、超时设置和输入文件的请求
        
    Returns:
        ExecuteResponse: 执行结果
    """
    try:
        # 验证请求
        if len(request.code.strip()) == 0:
            raise HTTPException(status_code=400, detail="代码不能为空")
        
        if len(request.code) > settings.MAX_CODE_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"代码长度不能超过 {settings.MAX_CODE_LENGTH} 字符"
            )
        
        if request.timeout > settings.MAX_TIMEOUT:
            raise HTTPException(
                status_code=400,
                detail=f"超时时间不能超过 {settings.MAX_TIMEOUT} 秒"
            )
        
        # 检查环境是否存在
        env = env_manager.get_environment(request.environment)
        if not env:
            raise HTTPException(status_code=404, detail=f"环境 '{request.environment}' 不存在")
        
        if env.status != "ready":
            raise HTTPException(
                status_code=400, 
                detail=f"环境 '{request.environment}' 状态为 {env.status}，无法使用"
            )
        
        # 执行代码
        result = await executor.execute(
            code=request.code,
            timeout=request.timeout,
            input_files=request.files or {},
            environment=request.environment
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return ExecuteResponse(
            success=False,
            stdout="",
            stderr="",
            execution_time=0.0,
            files={},
            error=f"执行出错: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
