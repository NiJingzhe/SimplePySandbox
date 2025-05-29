import tempfile
import shutil
import os
import re
from pathlib import Path
from typing import Optional


def create_secure_temp_dir() -> str:
    """创建安全的临时目录"""
    # 检测运行环境并选择合适的临时目录
    if os.path.exists("/app/data/temp"):
        # Docker环境中的共享临时目录
        base_temp_dir = "/app/data/temp"
        os.makedirs(base_temp_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp(prefix="sandbox_", dir=base_temp_dir)
    else:
        # 本地环境使用系统临时目录
        temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    
    # 设置目录权限
    os.chmod(temp_dir, 0o755)
    return temp_dir


def cleanup_temp_dir(temp_dir: str) -> None:
    """清理临时目录"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"清理临时目录失败: {e}")


def validate_filename(filename: str) -> bool:
    """
    验证文件名是否安全
    
    Args:
        filename: 要验证的文件名
        
    Returns:
        bool: 文件名是否安全
    """
    # 检查文件名长度
    if len(filename) > 255:
        return False
    
    # 检查是否包含危险字符
    dangerous_patterns = [
        r'\.\./',  # 路径遍历
        r'\.\.\\',  # Windows路径遍历
        r'^/',     # 绝对路径
        r'^[A-Z]:',  # Windows绝对路径
        r'[<>:"|?*]',  # Windows保留字符
        r'[\x00-\x1f]',  # 控制字符
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, filename):
            return False
    
    # 检查Windows保留文件名
    windows_reserved = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in windows_reserved:
        return False
    
    return True


def sanitize_output(text: str, max_length: int = 100000) -> str:
    """
    清理输出文本
    
    Args:
        text: 要清理的文本
        max_length: 最大长度
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length] + "\n... (输出被截断)"
    
    # 移除或替换危险字符
    text = text.replace('\x00', '')  # 移除null字符
    
    return text


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    ext = os.path.splitext(filename)[1].lower()
    # 如果扩展名只是一个点，返回空字符串
    return ext if ext != '.' else ''


def is_text_file(filename: str) -> bool:
    """判断是否为文本文件"""
    text_extensions = {
        '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
        '.md', '.rst', '.csv', '.log', '.ini', '.cfg', '.conf'
    }
    return get_file_extension(filename) in text_extensions


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
