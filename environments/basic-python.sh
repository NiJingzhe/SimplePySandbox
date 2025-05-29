#!/bin/bash
# 基础Python环境配置脚本
# 基础镜像建议: python:3.11-slim

set -e

echo "安装基础开发包..."

# 基础开发工具
pip install --no-cache-dir \
    requests \
    beautifulsoup4 \
    lxml \
    pillow \
    python-dateutil \
    pytz

echo "安装文件处理工具..."

# 文件和数据处理
pip install --no-cache-dir \
    openpyxl \
    xlsxwriter \
    pyyaml \
    toml \
    configparser

echo "安装实用工具..."

# 实用工具
pip install --no-cache-dir \
    click \
    rich \
    typer \
    loguru

echo "基础Python环境配置完成!"
