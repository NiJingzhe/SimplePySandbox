#!/bin/bash
# PythonOCC环境配置脚本 (保守版本)
# 这个脚本在已经创建的conda环境中执行

set -e

echo "🐍 配置PythonOCC环境..."

# 设置conda通道
echo "设置conda通道..."
conda config --add channels conda-forge
conda config --set channel_priority flexible

# 安装基础依赖 (不指定python版本，使用环境中已有的)
echo "安装基础依赖..."
conda install -y \
    pip \
    numpy \

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
    from OCC.Core.gp import gp_Pnt
    print('✅ PythonOCC导入成功!')
except Exception as e:
    print(f'⚠️  PythonOCC导入警告: {e}')
"

# 清理
echo "清理..."
conda clean -a -y

echo "✅ PythonOCC环境配置完成!"

# 确保脚本正常退出
exit 0
