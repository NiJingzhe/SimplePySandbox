#!/usr/bin/env python3
# filepath: /Users/lildino/Project/SimplePySandbox/examples/pythonocc_cylinder_example.py
"""
PythonOCC示例：创建圆柱体并导出为STEP格式

本示例展示如何：
1. 创建一个简单的圆柱体
2. 将其导出为STEP格式文件
"""

from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Vec
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.TCollection import TCollection_HAsciiString


def create_cylinder(radius=10.0, height=50.0):
    """
    创建一个圆柱体
    
    参数:
        radius: 圆柱体的半径
        height: 圆柱体的高度
    
    返回:
        圆柱体的TopoDS_Shape对象
    """
    # 在Z轴上创建圆柱体
    # 第一个点是基底中心点，第二个参数是圆柱体半径，第三个参数是圆柱体高度
    origin = gp_Pnt(0, 0, 0)  # 原点
    z_axis = gp_Dir(0, 0, 1)  # Z轴方向
    axis = gp_Ax2(origin, z_axis)  # 定义坐标系
    
    # 创建圆柱体
    cylinder = BRepPrimAPI_MakeCylinder(axis, radius, height).Shape()
    
    print(f"圆柱体已创建: 半径={radius}, 高度={height}")
    return cylinder


def export_to_step(shape, filename="cylinder.step"):
    """
    将形状导出为STEP文件
    
    参数:
        shape: 要导出的TopoDS_Shape对象
        filename: 输出文件名
    
    返回:
        bool: 是否成功导出
    """
    # 创建STEP导出器
    step_writer = STEPControl_Writer()
    
    # 设置STEP导出选项
    Interface_Static_SetCVal("write.step.schema", "AP214")
    
    # 将形状转换为STEP格式
    transfer_status = step_writer.Transfer(shape, STEPControl_AsIs)
    
    if transfer_status != IFSelect_RetDone:
        print("错误: 无法转换形状为STEP格式")
        return False
    
    # 写入文件
    write_status = step_writer.Write(filename)
    
    if write_status != IFSelect_RetDone:
        print(f"错误: 无法写入STEP文件 {filename}")
        return False
    
    print(f"STEP文件已成功导出至: {filename}")
    return True


def main():
    """主函数"""
    try:
        print("🔧 开始PythonOCC测试...")
        
        # 创建半径为15.0、高度为70.0的圆柱体
        print("📏 创建圆柱体...")
        cylinder_shape = create_cylinder(radius=15.0, height=70.0)
        print("✅ 成功创建圆柱体")
        
        # 导出为STEP文件
        print("💾 导出STEP文件...")
        success = export_to_step(cylinder_shape, "output_cylinder.step")
        if success:
            print("✅ 成功导出STEP文件")
        else:
            print("❌ STEP文件导出失败")
            
        print("🎉 PythonOCC测试完成")
        
    except Exception as e:
        print(f"❌ PythonOCC测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
