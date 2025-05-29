"""
安全策略模块
定义代码执行的安全限制和验证规则
"""

import ast
import re
from typing import List, Set


class SecurityPolicy:
    """安全策略类"""
    
    # 危险的内置函数和模块
    DANGEROUS_BUILTINS = {
        'eval', 'exec', 'compile', '__import__', 'open', 'input',
        'raw_input', 'file', 'reload', 'vars', 'dir', 'globals',
        'locals', 'memoryview', 'property', 'super', 'staticmethod',
        'classmethod', 'delattr', 'getattr', 'hasattr', 'setattr'
    }
    
    # 危险的模块
    DANGEROUS_MODULES = {
        'os', 'sys', 'subprocess', 'multiprocessing', 'threading',
        'socket', 'urllib', 'http', 'ftplib', 'telnetlib',
        'pickle', 'cPickle', 'marshal', 'shelve', 'dbm',
        'ctypes', 'imp', 'importlib', '__main__',
        'builtins', '__builtin__'
    }
    
    # 允许的安全模块
    SAFE_MODULES = {
        'math', 'random', 'datetime', 'time', 'json', 'base64',
        'hashlib', 'hmac', 'uuid', 'collections', 'itertools',
        'functools', 're', 'string', 'textwrap', 'unicodedata',
        'decimal', 'fractions', 'statistics', 'pathlib'
    }
    
    @classmethod
    def validate_code(cls, code: str) -> tuple[bool, str]:
        """
        验证代码是否安全
        
        Args:
            code: 要验证的代码
            
        Returns:
            tuple: (是否安全, 错误信息)
        """
        try:
            # 解析AST
            tree = ast.parse(code)
            
            # 检查AST节点
            for node in ast.walk(tree):
                if not cls._is_safe_node(node):
                    return False, f"检测到不安全的操作: {type(node).__name__}"
            
            # 检查字符串中的危险模式
            if not cls._check_string_patterns(code):
                return False, "检测到危险的字符串模式"
            
            return True, ""
            
        except SyntaxError as e:
            return False, f"语法错误: {str(e)}"
        except Exception as e:
            return False, f"代码验证失败: {str(e)}"
    
    @classmethod
    def _is_safe_node(cls, node: ast.AST) -> bool:
        """检查AST节点是否安全"""
        
        # 检查函数调用
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in cls.DANGEROUS_BUILTINS:
                    return False
        
        # 检查导入语句
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return cls._is_safe_import(node)
        
        # 检查属性访问
        if isinstance(node, ast.Attribute):
            return cls._is_safe_attribute(node)
        
        # 检查下标访问（可能访问__builtins__等）
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name) and node.value.id == '__builtins__':
                return False
        
        return True
    
    @classmethod
    def _is_safe_import(cls, node: ast.Import | ast.ImportFrom) -> bool:
        """检查导入是否安全"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in cls.DANGEROUS_MODULES:
                    return False
                # 检查是否为允许的模块
                if alias.name not in cls.SAFE_MODULES:
                    # 允许标准库的一些子模块
                    if not cls._is_safe_stdlib_module(alias.name):
                        return False
        
        elif isinstance(node, ast.ImportFrom):
            if node.module in cls.DANGEROUS_MODULES:
                return False
            if node.module and node.module not in cls.SAFE_MODULES:
                if not cls._is_safe_stdlib_module(node.module):
                    return False
        
        return True
    
    @classmethod
    def _is_safe_stdlib_module(cls, module_name: str) -> bool:
        """检查是否为安全的标准库模块"""
        safe_stdlib_patterns = [
            r'^collections\.',
            r'^urllib\.parse$',
            r'^email\.utils$',
            r'^html\.',
            r'^xml\.etree\.ElementTree$',
        ]
        
        for pattern in safe_stdlib_patterns:
            if re.match(pattern, module_name):
                return True
        
        return False
    
    @classmethod
    def _is_safe_attribute(cls, node: ast.Attribute) -> bool:
        """检查属性访问是否安全"""
        dangerous_attrs = {
            '__builtins__', '__globals__', '__locals__',
            '__dict__', '__class__', '__bases__', '__subclasses__',
            '__import__', '__file__', '__name__'
        }
        
        if node.attr in dangerous_attrs:
            return False
        
        return True
    
    @classmethod
    def _check_string_patterns(cls, code: str) -> bool:
        """检查代码字符串中的危险模式"""
        dangerous_patterns = [
            r'__builtins__',
            r'__import__',
            r'__globals__',
            r'__locals__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
            r'[\'"]eval[\'"]',  # 匹配 'eval' 或 "eval" 字符串
            r'[\'"]exec[\'"]',  # 匹配 'exec' 或 "exec" 字符串
            r'[\'"]__import__[\'"]',  # 匹配 '__import__' 字符串
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False
        
        return True


def create_safe_globals() -> dict:
    """创建安全的全局命名空间"""
    safe_builtins = {
        # 基本类型
        'bool', 'int', 'float', 'str', 'bytes', 'list', 'tuple', 'dict', 'set',
        'frozenset', 'complex', 'bytearray', 'memoryview',
        
        # 基本函数
        'abs', 'all', 'any', 'bin', 'chr', 'divmod', 'enumerate', 'filter',
        'format', 'hex', 'id', 'isinstance', 'issubclass', 'iter', 'len',
        'map', 'max', 'min', 'next', 'oct', 'ord', 'pow', 'range', 'repr',
        'reversed', 'round', 'slice', 'sorted', 'sum', 'zip',
        
        # 异常
        'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
        'AttributeError', 'NameError', 'RuntimeError', 'StopIteration',
        
        # 其他
        'print', 'help', 'copyright', 'credits', 'license', 'quit', 'exit'
    }
    
    # 创建受限的__builtins__
    restricted_builtins = {}
    import builtins
    
    for name in safe_builtins:
        if hasattr(builtins, name):
            restricted_builtins[name] = getattr(builtins, name)
    
    return {
        '__builtins__': restricted_builtins,
        '__name__': '__main__',
        '__doc__': None,
    }
