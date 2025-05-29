# SimplePySandbox Dockerfile
# 使用Python 3.11避免pydantic-core兼容性问题
FROM continuumio/miniconda3:23.10.0-1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 创建Python 3.11环境
RUN conda create -n sandbox python=3.11 -y && \
    conda clean -afy

# 激活环境并设置为默认
SHELL ["conda", "run", "-n", "sandbox", "/bin/bash", "-c"]
ENV PATH /opt/conda/envs/sandbox/bin:$PATH

# 更新pip
RUN pip install --upgrade pip setuptools wheel

# 复制requirements.txt并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p data/environments logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV EXECUTION_MODE=conda
ENV HOST=0.0.0.0
ENV PORT=8000

# 创建非root用户并设置权限
RUN groupadd -r sandbox && \
    useradd -r -g sandbox -u 1000 -m sandbox && \
    chown -R sandbox:sandbox /app && \
    chmod -R 755 /app && \
    mkdir -p /home/sandbox/.conda && \
    chown -R sandbox:sandbox /home/sandbox/.conda && \
    chmod -R 755 /home/sandbox/.conda && \
    mkdir -p /app/data/conda_envs && \
    chown -R sandbox:sandbox /app/data/conda_envs

# 切换到非root用户
USER sandbox

# 配置conda环境目录 - 使用用户级别的目录
RUN conda config --add envs_dirs /app/data/conda_envs && \
    conda config --add envs_dirs /home/sandbox/.conda/envs && \
    conda config --set auto_activate_base false

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
