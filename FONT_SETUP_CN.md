# Ubuntu 系统中文字体设置指南

## 问题描述

在 Ubuntu 系统上运行 ComfyUI-iyunya-nodes 的文字叠加功能时，可能会遇到中文显示乱码的问题。这是因为系统缺少合适的中文字体。

## 解决方案

### 方法一：自动安装脚本（推荐）

1. 进入节点目录：
```bash
cd custom_nodes/ComfyUI-iyunya-nodes
```

2. 运行自动安装脚本：
```bash
sudo bash install_fonts.sh
```

### 方法二：手动安装

#### 安装 Noto CJK 字体（推荐）
```bash
sudo apt-get update
sudo apt-get install fonts-noto-cjk
```

#### 安装文泉驿字体
```bash
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
```

#### 安装文鼎字体
```bash
sudo apt-get install fonts-arphic-ukai fonts-arphic-uming
```

#### 刷新字体缓存
```bash
fc-cache -fv
```

### 方法三：使用自定义字体

如果您有特定的中文字体文件（.ttf 或 .ttc 格式），可以：

1. 将字体文件复制到系统字体目录：
```bash
sudo cp your-font.ttf /usr/share/fonts/truetype/
sudo fc-cache -fv
```

2. 或者在节点设置中直接指定字体文件路径。

## 验证安装

### 使用字体检测脚本
```bash
cd custom_nodes/ComfyUI-iyunya-nodes
python3 check_fonts.py
```

### 手动检查已安装的中文字体
```bash
fc-list | grep -i 'noto\|wqy\|arphic' | head -10
```

## 支持的字体

修改后的代码现在支持以下中文字体（按优先级排序）：

1. **Noto Sans CJK** - Google 开源字体，支持中日韩文字
2. **Noto Serif CJK** - Noto 系列的衬线字体
3. **文泉驿微米黑** - 开源中文字体
4. **文泉驿正黑** - 开源中文字体
5. **文鼎楷书** - 文鼎字体公司的楷书字体
6. **文鼎明体** - 文鼎字体公司的明体字体

## 常见问题

### Q: 安装字体后仍然显示乱码怎么办？
A: 
1. 确保重启了 ComfyUI 服务
2. 运行 `fc-cache -fv` 刷新字体缓存
3. 使用检测脚本验证字体是否正确安装

### Q: 可以使用自定义字体吗？
A: 可以，在文字叠加节点的设置中，有一个 `font_path` 参数，您可以指定自定义字体文件的完整路径。

### Q: 在 Docker 容器中如何安装字体？
A: 在 Dockerfile 中添加：
```dockerfile
RUN apt-get update && \
    apt-get install -y fonts-noto-cjk fonts-wqy-microhei && \
    fc-cache -fv
```

### Q: 字体大小如何调整？
A: 节点提供三种字体大小模式：
- `auto_fit`: 自动适应边界框大小
- `max_fill`: 最大化填充边界框
- `fixed`: 使用固定字体大小

## 技术说明

修改后的代码包含以下改进：

1. **增强的字体检测**: 添加了更多常见的 Linux 中文字体路径
2. **字体优先级**: 中文字体优先于西文字体
3. **详细的错误提示**: 当找不到字体时，提供具体的安装建议
4. **字体检测工具**: 提供独立的字体检测和测试脚本

## 更新日志

- 添加了对多种常见 Linux 中文字体的支持
- 改进了字体检测和加载逻辑
- 提供了自动安装脚本和检测工具
- 增加了详细的错误提示和安装指导 