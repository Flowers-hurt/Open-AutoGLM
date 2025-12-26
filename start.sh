#!/bin/bash
# Phone Agent 启动脚本
# 此脚本用于快速启动 Phone Agent 项目

echo "=================================="
echo "Phone Agent 启动脚本"
echo "=================================="
echo ""

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查ADB设备连接
echo ""
echo "🔍 检查ADB设备连接..."
adb devices

# 显示使用说明
echo ""
echo "=================================="
echo "✅ 环境准备完成！"
echo "=================================="
echo ""
echo "使用说明："
echo ""
echo "1. 确保你的Android设备已连接并开启USB调试"
echo "   运行: adb devices"
echo ""
echo "2. 启动模型服务（选择以下方式之一）："
echo ""
echo "   方式A - 使用第三方API服务："
echo "   - 智谱BigModel: https://open.bigmodel.cn"
echo "   - ModelScope: https://modelscope.cn"
echo ""
echo "   方式B - 本地部署模型："
echo "   - 参考 README.md 中的模型部署章节"
echo ""
echo "3. 运行Phone Agent："
echo ""
echo "   # 使用智谱BigModel API"
echo "   python main.py --base-url https://open.bigmodel.cn/api/paas/v4 \\"
echo "     --model autoglm-phone --apikey 你的API密钥 \\"
echo "     \"打开美团搜索附近的火锅店\""
echo ""
echo "   # 使用本地模型服务"
echo "   python main.py --base-url http://localhost:8000/v1 \\"
echo "     --model autoglm-phone-9b \\"
echo "     \"打开美团搜索附近的火锅店\""
echo ""
echo "   # 进入交互模式"
echo "   python main.py --base-url http://localhost:8000/v1 \\"
echo "     --model autoglm-phone-9b"
echo ""
echo "4. 查看更多选项："
echo "   python main.py --help"
echo ""
echo "=================================="
