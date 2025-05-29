import pytest
from sandbox.security import SecurityPolicy, create_safe_globals

pytestmark = pytest.mark.unit


class TestSecurityPolicy:
    """安全策略测试"""

    def test_safe_code(self):
        """测试安全代码"""
        safe_codes = [
            "print('Hello, World!')",
            "import math\nresult = math.sqrt(16)",
            "import json\ndata = {'key': 'value'}",
            "x = 1 + 2\nprint(x)",
            "for i in range(10):\n    print(i)",
        ]

        for code in safe_codes:
            is_safe, error = SecurityPolicy.validate_code(code)
            assert is_safe, f"代码应该是安全的: {code}, 错误: {error}"

    def test_dangerous_builtins(self):
        """测试危险的内置函数"""
        dangerous_codes = [
            "eval('1+1')",
            "exec('print(1)')",
            "__import__('os')",
            "compile('1+1', '<string>', 'eval')",
        ]

        for code in dangerous_codes:
            is_safe, error = SecurityPolicy.validate_code(code)
            assert not is_safe, f"代码应该被标记为不安全: {code}"

    def test_dangerous_modules(self):
        """测试危险模块导入"""
        dangerous_codes = [
            "import os",
            "import sys",
            "import subprocess",
            "from os import system",
            "import socket",
        ]

        for code in dangerous_codes:
            is_safe, error = SecurityPolicy.validate_code(code)
            assert not is_safe, f"代码应该被标记为不安全: {code}"

    def test_safe_modules(self):
        """测试安全模块导入"""
        safe_codes = [
            "import math",
            "import json",
            "import datetime",
            "from math import sqrt",
            "import random",
        ]

        for code in safe_codes:
            is_safe, error = SecurityPolicy.validate_code(code)
            assert is_safe, f"代码应该是安全的: {code}, 错误: {error}"

    def test_dangerous_attributes(self):
        """测试危险属性访问"""
        dangerous_codes = [
            "x.__class__",
            "x.__globals__",
            "x.__builtins__",
            "[].__class__.__bases__[0].__subclasses__()",
        ]

        for code in dangerous_codes:
            is_safe, error = SecurityPolicy.validate_code(code)
            assert not is_safe, f"代码应该被标记为不安全: {code}"

    def test_syntax_error(self):
        """测试语法错误"""
        is_safe, error = SecurityPolicy.validate_code("print('missing quote")
        assert not is_safe
        assert "语法错误" in error

    def test_string_patterns(self):
        """测试字符串中的危险模式"""
        dangerous_codes = [
            "# This code uses __builtins__",
            "x = '__import__'",
            "func = 'eval'",
        ]

        for code in dangerous_codes:
            is_safe, error = SecurityPolicy.validate_code(code)
            assert not is_safe, f"代码应该被标记为不安全: {code}"


class TestSafeGlobals:
    """安全全局命名空间测试"""

    def test_create_safe_globals(self):
        """测试创建安全的全局命名空间"""
        globals_dict = create_safe_globals()

        assert '__builtins__' in globals_dict
        assert '__name__' in globals_dict
        assert globals_dict['__name__'] == '__main__'

        # 检查安全的内置函数存在
        builtins = globals_dict['__builtins__']
        safe_functions = ['print', 'len', 'range', 'str', 'int', 'float']
        for func in safe_functions:
            assert func in builtins

        # 检查危险函数不存在
        dangerous_functions = ['eval', 'exec', '__import__', 'open']
        for func in dangerous_functions:
            assert func not in builtins