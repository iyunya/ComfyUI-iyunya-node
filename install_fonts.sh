#!/bin/bash

# ComfyUI-iyunya-nodes 中文字体安装脚本
# 适用于 Ubuntu/Debian 系统

echo "=== ComfyUI-iyunya-nodes 中文字体安装脚本 ==="
echo

# 检查是否为 root 用户或有 sudo 权限
if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    echo "错误: 需要 sudo 权限来安装字体包"
    echo "请使用 sudo 运行此脚本："
    echo "sudo bash install_fonts.sh"
    exit 1
fi

echo "正在更新包列表..."
sudo apt-get update

echo
echo "正在安装中文字体包..."

# 安装 Noto CJK 字体（推荐，支持中日韩文字）
echo "- 安装 Noto CJK 字体..."
sudo apt-get install -y fonts-noto-cjk

# 安装文泉驿字体
echo "- 安装文泉驿微米黑字体..."
sudo apt-get install -y fonts-wqy-microhei

echo "- 安装文泉驿正黑字体..."
sudo apt-get install -y fonts-wqy-zenhei

# 安装文鼎字体
echo "- 安装文鼎楷书字体..."
sudo apt-get install -y fonts-arphic-ukai

echo "- 安装文鼎明体字体..."
sudo apt-get install -y fonts-arphic-uming

echo
echo "正在刷新字体缓存..."
fc-cache -fv

echo
echo "=== 字体安装完成 ==="
echo
echo "已安装的中文字体："
echo "- Noto Sans CJK (推荐)"
echo "- 文泉驿微米黑"
echo "- 文泉驿正黑"
echo "- 文鼎楷书"
echo "- 文鼎明体"
echo
echo "现在可以重新运行 ComfyUI，中文应该能正常显示了。"
echo
echo "如果仍有问题，可以通过以下命令检查已安装的字体："
echo "fc-list | grep -i 'noto\\|wqy\\|arphic' | head -10" 