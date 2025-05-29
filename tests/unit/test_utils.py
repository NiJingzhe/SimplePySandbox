import pytest
import tempfile
import os
from sandbox.utils import (
    create_secure_temp_dir, cleanup_temp_dir, validate_filename,
    sanitize_output, get_file_extension, is_text_file, format_file_size
)

pytestmark = pytest.mark.unit

class TestTempDirManagement:
    """临时目录管理测试"""

    def test_create_secure_temp_dir(self):
        """测试创建安全临时目录"""
        temp_dir = create_secure_temp_dir()
        
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        assert "sandbox_" in os.path.basename(temp_dir)
        
        # 清理
        cleanup_temp_dir(temp_dir)
        assert not os.path.exists(temp_dir)

    def test_cleanup_temp_dir(self):
        """测试清理临时目录"""
        temp_dir = create_secure_temp_dir()
        
        # 创建一些文件
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        assert os.path.exists(test_file)
        
        # 清理
        cleanup_temp_dir(temp_dir)
        assert not os.path.exists(temp_dir)
        assert not os.path.exists(test_file)

    def test_cleanup_nonexistent_dir(self):
        """测试清理不存在的目录"""
        # 应该不会抛出异常
        cleanup_temp_dir("/nonexistent/directory")


class TestFilenameValidation:
    """文件名验证测试"""

    def test_valid_filenames(self):
        """测试有效文件名"""
        valid_names = [
            "test.txt",
            "data.json",
            "output.csv",
            "script.py",
            "file_with_underscore.txt",
            "file-with-dash.txt",
            "file.with.dots.txt",
        ]
        
        for name in valid_names:
            assert validate_filename(name), f"文件名应该有效: {name}"

    def test_invalid_filenames(self):
        """测试无效文件名"""
        invalid_names = [
            "../../../etc/passwd",  # 路径遍历
            "..\\windows\\system32",  # Windows路径遍历
            "/absolute/path.txt",  # 绝对路径
            "C:\\Windows\\system.ini",  # Windows绝对路径
            "file<name>.txt",  # 包含危险字符
            "file|name.txt",  # 管道字符
            "file?name.txt",  # 问号
            "file*name.txt",  # 通配符
            "CON.txt",  # Windows保留名
            "PRN.txt",  # Windows保留名
            "AUX.txt",  # Windows保留名
            "a" * 300,  # 文件名过长
        ]
        
        for name in invalid_names:
            assert not validate_filename(name), f"文件名应该无效: {name}"


class TestOutputSanitization:
    """输出清理测试"""

    def test_sanitize_normal_output(self):
        """测试正常输出清理"""
        text = "Hello, World!\nThis is a test."
        result = sanitize_output(text)
        assert result == text

    def test_sanitize_empty_output(self):
        """测试空输出"""
        assert sanitize_output("") == ""

    def test_sanitize_long_output(self):
        """测试长输出截断"""
        long_text = "A" * 200000
        result = sanitize_output(long_text, max_length=1000)
        assert len(result) <= 1020  # 1000 + 截断提示
        assert "输出被截断" in result

    def test_sanitize_dangerous_chars(self):
        """测试危险字符清理"""
        text_with_null = "Hello\x00World"
        result = sanitize_output(text_with_null)
        assert "\x00" not in result
        assert result == "HelloWorld"


class TestFileExtensions:
    """文件扩展名测试"""

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        test_cases = [
            ("file.txt", ".txt"),
            ("script.py", ".py"),
            ("data.JSON", ".json"),  # 测试大小写
            ("file.tar.gz", ".gz"),
            ("noextension", ""),
            (".hidden", ""),
            ("file.", ""),
        ]
        
        for filename, expected in test_cases:
            assert get_file_extension(filename) == expected

    def test_is_text_file(self):
        """测试判断文本文件"""
        text_files = [
            "script.py", "data.txt", "config.json", "style.css",
            "page.html", "readme.md", "data.csv", "app.log"
        ]
        
        binary_files = [
            "image.jpg", "video.mp4", "archive.zip", "binary.exe",
            "document.pdf", "audio.mp3"
        ]
        
        for filename in text_files:
            assert is_text_file(filename), f"应该被识别为文本文件: {filename}"
        
        for filename in binary_files:
            assert not is_text_file(filename), f"应该被识别为二进制文件: {filename}"


class TestFileSizeFormatting:
    """文件大小格式化测试"""

    def test_format_file_size(self):
        """测试文件大小格式化"""
        test_cases = [
            (0, "0 B"),
            (512, "512 B"),
            (1024, "1.0 KB"),
            (1536, "1.5 KB"),
            (1048576, "1.0 MB"),
            (1572864, "1.5 MB"),
            (2097152, "2.0 MB"),
        ]
        
        for size_bytes, expected in test_cases:
            result = format_file_size(size_bytes)
            assert result == expected, f"大小 {size_bytes} 应该格式化为 {expected}, 但得到 {result}"