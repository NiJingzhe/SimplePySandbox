"""
pytest配置文件
定义测试装置和全局测试配置
"""
import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def project_root():
    """返回项目根目录路径"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir():
    """返回测试数据目录路径"""
    return Path(__file__).parent / "data"

@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_path = tempfile.mkdtemp(prefix="sandbox_test_")
    yield temp_path
    # 清理
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)

@pytest.fixture
def sample_code():
    """提供示例代码用于测试"""
    return {
        "simple": "print('Hello, World!')",
        "math": "import math\nresult = math.sqrt(16)\nprint(f'Result: {result}')",
        "error": "raise ValueError('Test error')",
        "timeout": "import time\ntime.sleep(10)",
        "file_ops": """
import os
with open('test.txt', 'w') as f:
    f.write('Hello from file')
with open('test.txt', 'r') as f:
    content = f.read()
print(content)
os.remove('test.txt')
"""
    }

@pytest.fixture
def api_base_url():
    """API基础URL"""
    return os.getenv("API_BASE_URL", "http://localhost:8000")

# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "system: 系统测试"
    )
    config.addinivalue_line(
        "markers", "performance: 性能测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "requires_docker: 需要Docker环境的测试"
    )
