#!/bin/bash
# 快捷启动脚本

echo "=========================================="
echo "云效到 K8s 镜像版本自动更新工具"
echo "=========================================="

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3,请先安装 Python 3.8+"
    exit 1
fi

# 检查依赖
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "⚠️  检测到依赖未安装,正在安装..."
    pip3 install -r requirements.txt
    playwright install chromium
fi

# 运行主程序
echo ""
echo "🚀 启动中..."
echo ""
python3 main.py
