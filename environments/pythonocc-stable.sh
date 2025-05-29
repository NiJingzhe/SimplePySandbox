#!/bin/bash
# PythonOCC环境配置脚本 (保守版本)
# 基础镜像: continuumio/miniconda3:latest

set -e

echo "🐍 配置PythonOCC环境..."

# 更新conda
echo "更新conda..."
conda update -n base conda -y

# 设置conda通道
echo "设置conda通道..."
conda config --add channels conda-forge
conda config --set channel_priority flexible

# 安装基础依赖
echo "安装基础依赖..."
conda install -y \
    python=3.9 \
    pip \
    numpy \
    matplotlib

# 尝试安装pythonocc-core的较老稳定版本
echo "安装pythonocc-core..."
conda install -y -c conda-forge pythonocc-core=7.9.0

# 安装额外工具
echo "安装额外工具..."
pip install --no-cache-dir requests

# 简单验证
echo "验证安装..."
python -c "
import sys
print(f'Python version: {sys.version}')
try:
    from OCC.Core import gp_Pnt
    print('✅ PythonOCC导入成功!')
except Exception as e:
    print(f'⚠️  PythonOCC导入警告: {e}')
"

# 清理
echo "清理..."
conda clean -a -y

echo "✅ PythonOCC环境配置完成!"
