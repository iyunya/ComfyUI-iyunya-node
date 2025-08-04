#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ComfyUI-iyunya-nodes 字体检测脚本
用于检查系统中可用的中文字体
"""

import os
import platform
from PIL import ImageFont

def detect_fonts():
    """检测系统中可用的字体"""
    system = platform.system()
    print(f"检测系统: {system}")
    print("=" * 50)
    
    # 定义字体路径
    if system == "Windows":
        font_paths = [
            ("微软雅黑", "C:/Windows/Fonts/msyh.ttc"),
            ("黑体", "C:/Windows/Fonts/simhei.ttf"),
            ("宋体", "C:/Windows/Fonts/simsun.ttc"),
            ("Arial", "C:/Windows/Fonts/arial.ttf"),
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            ("苹方", "/System/Library/Fonts/PingFang.ttc"),
            ("Helvetica", "/System/Library/Fonts/Helvetica.ttc"),
            ("Arial", "/System/Library/Fonts/Arial.ttf"),
        ]
    else:  # Linux
        font_paths = [
            ("Noto Sans CJK", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
            ("Noto Sans CJK (OpenType)", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            ("Noto Serif CJK", "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc"),
            ("Noto Serif CJK (OpenType)", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"),
            ("文泉驿微米黑", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
            ("文泉驿正黑", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
            ("文鼎楷书", "/usr/share/fonts/truetype/arphic/ukai.ttc"),
            ("文鼎明体", "/usr/share/fonts/truetype/arphic/uming.ttc"),
            ("DejaVu Sans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ("Liberation Sans", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            ("DejaVu Sans (TTF)", "/usr/share/fonts/TTF/DejaVuSans.ttf"),
            ("Liberation Sans (System)", "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"),
        ]
    
    available_fonts = []
    missing_fonts = []
    
    print("字体检测结果:")
    print("-" * 50)
    
    for name, path in font_paths:
        if os.path.exists(path):
            print(f"✓ {name}: {path}")
            available_fonts.append((name, path))
            
            # 测试字体是否可以正常加载
            try:
                font = ImageFont.truetype(path, 16)
                print(f"  → 字体加载测试: 成功")
            except Exception as e:
                print(f"  → 字体加载测试: 失败 ({e})")
        else:
            print(f"✗ {name}: {path} (未找到)")
            missing_fonts.append((name, path))
    
    print("\n" + "=" * 50)
    print(f"检测完成: 找到 {len(available_fonts)} 个字体，缺少 {len(missing_fonts)} 个字体")
    
    if available_fonts:
        print(f"\n推荐使用字体: {available_fonts[0][0]}")
        print(f"字体路径: {available_fonts[0][1]}")
    
    if missing_fonts and system == "Linux":
        print("\n如果中文显示有问题，建议安装以下字体包:")
        print("sudo apt-get install fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei")
        print("sudo apt-get install fonts-arphic-ukai fonts-arphic-uming")
        print("\n或者运行字体安装脚本:")
        print("bash install_fonts.sh")
    
    return available_fonts

def test_chinese_text():
    """测试中文文字渲染"""
    available_fonts = detect_fonts()
    
    if not available_fonts:
        print("\n警告: 没有找到可用的字体，中文可能无法正确显示")
        return
    
    print(f"\n测试中文文字渲染...")
    print("-" * 30)
    
    test_text = "测试中文字体显示效果"
    font_path = available_fonts[0][1]
    
    try:
        from PIL import Image, ImageDraw
        
        # 创建测试图像
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # 加载字体
        font = ImageFont.truetype(font_path, 24)
        
        # 绘制文字
        draw.text((10, 30), test_text, font=font, fill='black')
        
        # 保存测试图像
        img.save('font_test.png')
        print(f"✓ 中文字体测试成功")
        print(f"✓ 测试图像已保存为: font_test.png")
        print(f"✓ 使用字体: {available_fonts[0][0]}")
        
    except Exception as e:
        print(f"✗ 中文字体测试失败: {e}")

if __name__ == "__main__":
    print("ComfyUI-iyunya-nodes 字体检测工具")
    print("=" * 50)
    
    try:
        test_chinese_text()
    except ImportError:
        print("PIL 模块未安装，只进行字体路径检测")
        detect_fonts()
    
    print("\n检测完成!") 