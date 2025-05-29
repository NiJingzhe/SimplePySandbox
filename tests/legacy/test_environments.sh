#!/bin/bash
# filepath: /Users/lildino/Project/SimplePySandbox/test_environments.sh
# 环境功能测试脚本

set -e

echo "🧪 开始环境功能测试..."

# 检查API是否运行
echo "1. 检查API服务..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API服务正常运行"
else
    echo "❌ API服务未运行，请先启动服务"
    echo "   运行: docker-compose up -d"
    exit 1
fi

# 测试创建基础Python环境
echo
echo "2. 创建基础Python环境..."
python3 manage_environments.py create basic-test environments/basic-python.sh \
    --description "基础Python测试环境" \
    --wait --wait-timeout 5

# 列出所有环境
echo
echo "3. 列出所有环境..."
python3 manage_environments.py list

# 测试在新环境中执行代码
echo
echo "4. 在基础环境中测试代码执行..."
curl -X POST "http://localhost:8000/execute-with-environment" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import requests\nimport yaml\nprint(\"✅ 基础包导入成功\")\nprint(f\"Requests版本: {requests.__version__}\")",
    "environment": "basic-test",
    "timeout": 30
  }' | python3 -m json.tool

echo
echo "5. 清理测试环境..."
python3 manage_environments.py delete basic-test

echo
echo "🎉 环境功能测试完成!"
echo
echo "💡 使用示例:"
echo "   # 创建数据科学环境"
echo "   python3 manage_environments.py create data-sci environments/data-science-pip.sh --wait"
echo
echo "   # 在环境中执行代码"
echo "   curl -X POST http://localhost:8000/execute-with-environment \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"code\": \"import pandas as pd\\nprint(pd.__version__)\", \"environment\": \"data-sci\"}'"
echo
echo "   # 查看环境详情"
echo "   python3 manage_environments.py info data-sci"
echo
echo "   # 删除环境"
echo "   python3 manage_environments.py delete data-sci"
