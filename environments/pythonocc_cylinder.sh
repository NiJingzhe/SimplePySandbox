#!/bin/bash
# filepath: /Users/lildino/Project/SimplePySandbox/environments/pythonocc_cylinder.sh
# 简化的PythonOCC环境构建脚本，用于创建和导出圆柱体

set -e

# 安装Python 3.9和Miniconda
apt-get update
apt-get install -y wget bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 git mercurial subversion

# 获取并安装Miniconda
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p /opt/conda
rm /tmp/miniconda.sh
ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
echo "conda activate base" >> ~/.bashrc
. /opt/conda/etc/profile.d/conda.sh
conda activate base

# 创建pythonocc环境
conda create -y -n pythonocc python=3.9
conda activate pythonocc

# 安装PythonOCC和必要的依赖
conda install -y -c conda-forge pythonocc-core=7.6.3

# 创建一个简单的测试脚本，确认安装成功
cat > /tmp/test_occ.py << 'EOF'
try:
    from OCC.Core.gp import gp_Pnt
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
    print("PythonOCC导入成功!")
except ImportError as e:
    print(f"导入错误: {e}")
    exit(1)

point = gp_Pnt(0, 0, 0)
sphere = BRepPrimAPI_MakeSphere(point, 10).Shape()
print("成功创建了一个球体!")
print("PythonOCC-Core 安装验证完成!")
EOF

# 运行测试
python /tmp/test_occ.py

# 清理
rm /tmp/test_occ.py

# 设置环境变量
echo '#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate pythonocc
export PYTHONPATH=/opt/conda/envs/pythonocc/lib/python3.9/site-packages:$PYTHONPATH
' > /etc/environment.sh

echo "PythonOCC环境安装完成!"
