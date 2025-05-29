#!/bin/bash
# PythonOCC环境测试 - cURL命令 (修复版)

echo "🧪 PythonOCC环境直接测试"
echo "=========================="

BASE_URL="http://localhost:8000"

# 1. 检查API健康状态
echo "1. 检查API健康状态..."
curl -s -X GET "$BASE_URL/health" | python3 -m json.tool

echo -e "\n2. 列出所有可用环境..."
curl -s -X GET "$BASE_URL/environments" | python3 -m json.tool

echo -e "\n3. 检查pythonocc-stable环境详情..."
curl -s -X GET "$BASE_URL/environments/pythonocc-stable" | python3 -m json.tool

echo -e "\n4. 测试基础Python导入..."
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import sys; print(f\"Python version: {sys.version}\"); import platform; print(f\"Platform: {platform.platform()}\")",
    "environment": "pythonocc-stable",
    "timeout": 30
  }' | python3 -m json.tool

echo -e "\n5. 测试PythonOCC核心导入..."
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "try:\n    from OCC.Core.gp import gp_Pnt, gp_Dir\n    print(\"✅ PythonOCC Core导入成功\")\n    print(f\"gp_Pnt: {gp_Pnt}\")\nexcept Exception as e:\n    print(f\"❌ PythonOCC导入失败: {e}\")\n    import traceback\n    traceback.print_exc()",
    "environment": "pythonocc-stable",
    "timeout": 30
  }' | python3 -m json.tool

echo -e "\n6. 测试完整PythonOCC圆柱体创建..."

# 创建临时JSON文件避免控制字符问题
cat > /tmp/pythonocc_test.json << 'EOF'
{
  "code": "try:\n    print('🔧 开始PythonOCC测试...')\n    \n    # 导入所需模块\n    from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir\n    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder\n    from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs\n    from OCC.Core.IFSelect import IFSelect_RetDone\n    from OCC.Core.Interface import Interface_Static_SetCVal\n    print('✅ 成功导入所有模块')\n    \n    # 创建圆柱体\n    print('📏 创建圆柱体...')\n    origin = gp_Pnt(0, 0, 0)\n    z_axis = gp_Dir(0, 0, 1)\n    axis = gp_Ax2(origin, z_axis)\n    cylinder = BRepPrimAPI_MakeCylinder(axis, 10.0, 30.0).Shape()\n    print('✅ 成功创建圆柱体')\n    \n    # 创建STEP导出器\n    print('💾 导出STEP文件...')\n    step_writer = STEPControl_Writer()\n    Interface_Static_SetCVal('write.step.schema', 'AP214')\n    transfer_status = step_writer.Transfer(cylinder, STEPControl_AsIs)\n    \n    if transfer_status == IFSelect_RetDone:\n        write_status = step_writer.Write('test_cylinder.step')\n        if write_status == IFSelect_RetDone:\n            print('✅ 成功导出STEP文件')\n        else:\n            print('❌ STEP文件写入失败')\n    else:\n        print('❌ STEP转换失败')\n    \n    print('🎉 PythonOCC测试完成')\n    \nexcept Exception as e:\n    print(f'❌ 测试失败: {e}')\n    import traceback\n    traceback.print_exc()",
  "environment": "pythonocc-stable",
  "timeout": 60
}
EOF

curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d @/tmp/pythonocc_test.json | python3 -m json.tool

echo -e "\n7. 使用基础execute端点测试简单代码..."
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello from pythonocc-stable environment!\")",
    "environment": "pythonocc-stable",
    "timeout": 30
  }' | python3 -m json.tool

echo -e "\n8. 测试环境是否存在..."
curl -s -X GET "$BASE_URL/environments/pythonocc-stable" | python3 -m json.tool

# 清理临时文件
rm -f /tmp/pythonocc_test.json

echo -e "\n✅ PythonOCC环境测试完成!"