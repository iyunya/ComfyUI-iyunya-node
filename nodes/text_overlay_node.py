import os
import json
import logging
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import platform

logger = logging.getLogger("text_overlay")

class TextOverlayNode:
    """
    文字叠加显示节点 - 将OCR识别的文字内容显示在图片上
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "ocr_json": ("STRING", {
                    "multiline": True,
                    "tooltip": "OCR识别结果的JSON字符串"
                }),
                            "font_size_mode": (["auto_fit", "max_fill", "fixed"], {
                "default": "auto_fit",
                "tooltip": "字体大小模式：auto_fit自动适应bbox，max_fill最大化填充，fixed固定大小"
            }),
                "font_size": ("INT", {
                    "default": 16,
                    "min": 8,
                    "max": 100,
                    "step": 1,
                    "tooltip": "固定模式下的文字大小"
                }),
                            "fill_ratio": ("FLOAT", {
                "default": 0.95,
                "min": 0.1,
                "max": 1.0,
                "step": 0.05,
                "tooltip": "自动模式下文字相对于bbox的填充比例"
            }),
                "text_color": (["red", "green", "blue", "white", "black", "yellow", "cyan", "magenta"], {
                    "default": "red",
                    "tooltip": "文字颜色"
                }),
                "background_color": (["none", "white", "black", "yellow", "green", "blue", "red"], {
                    "default": "none",
                    "tooltip": "文字背景色，none表示透明"
                }),
                "position_mode": (["bbox_top", "bbox_center", "bbox_bottom", "bbox_left", "bbox_right"], {
                    "default": "bbox_top",
                    "tooltip": "文字显示位置相对于边界框的位置"
                }),
                "enable_stroke": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "透明背景时是否启用文字描边以提高可读性"
                })
            },
            "optional": {
                "text_alpha": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "文字透明度"
                }),
                "font_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "自定义字体文件路径，留空使用系统默认字体"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("overlay_image",)
    FUNCTION = "overlay_text"
    CATEGORY = "iyunya/文字处理"
    
    def tensor_to_pil(self, tensor):
        """将tensor转换为PIL图像"""
        if len(tensor.shape) == 4:
            tensor = tensor[0]  # 取第一张图片
        
        image_np = tensor.cpu().numpy()
        if image_np.max() <= 1.0:
            image_np = (image_np * 255).astype(np.uint8)
        else:
            image_np = image_np.astype(np.uint8)
            
        return Image.fromarray(image_np)
    
    def pil_to_tensor(self, pil_image):
        """将PIL图像转换为tensor"""
        image_np = np.array(pil_image).astype(np.float32) / 255.0
        return torch.from_numpy(image_np).unsqueeze(0)
    
    def get_font(self, font_size, font_path=""):
        """获取字体对象"""
        try:
            if font_path and os.path.exists(font_path):
                # 使用自定义字体
                return ImageFont.truetype(font_path, font_size)
            else:
                # 尝试使用系统字体
                system = platform.system()
                if system == "Windows":
                    # Windows系统字体路径
                    font_paths = [
                        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                        "C:/Windows/Fonts/simhei.ttf",  # 黑体
                        "C:/Windows/Fonts/simsun.ttc",  # 宋体
                        "C:/Windows/Fonts/arial.ttf",  # Arial
                    ]
                elif system == "Darwin":  # macOS
                    font_paths = [
                        "/System/Library/Fonts/PingFang.ttc",  # 苹方
                        "/System/Library/Fonts/Helvetica.ttc",  # Helvetica
                        "/System/Library/Fonts/Arial.ttf",  # Arial
                    ]
                else:  # Linux
                    font_paths = [
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                    ]
                
                # 尝试加载系统字体
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            return ImageFont.truetype(font_path, font_size)
                        except Exception:
                            continue
                
                # 如果都失败了，使用默认字体
                logger.warning("无法加载系统字体，使用PIL默认字体")
                return ImageFont.load_default()
                
        except Exception as e:
            logger.warning(f"字体加载失败：{str(e)}，使用默认字体")
            return ImageFont.load_default()
    
    def get_font_path(self, font_path=""):
        """获取字体文件路径"""
        if font_path and os.path.exists(font_path):
            return font_path
        
        # 获取系统字体路径
        system = platform.system()
        if system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf", 
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/arial.ttf",
            ]
        elif system == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def calculate_auto_font_size(self, text, bbox, fill_ratio, font_path=""):
        """自动计算适合bbox的字体大小"""
        x1, y1, x2, y2 = bbox
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        
        # 目标尺寸，使用更高的填充率
        target_width = int(bbox_width * fill_ratio)
        target_height = int(bbox_height * fill_ratio)
        
        # 字体大小搜索范围
        min_size = 6
        max_size = min(500, max(bbox_width, bbox_height))  # 根据bbox大小调整最大字体
        best_size = min_size
        
        # 获取字体路径
        font_file_path = self.get_font_path(font_path)
        
        # 二分查找最佳字体大小 - 提高精度
        left, right = min_size, max_size
        
        while right - left > 1:  # 精确到1像素
            mid_size = (left + right) // 2
            
            try:
                # 测试字体
                if font_file_path:
                    test_font = ImageFont.truetype(font_file_path, mid_size)
                else:
                    test_font = ImageFont.load_default()
                
                # 创建临时绘制对象来测量文字尺寸
                temp_img = Image.new('RGB', (max(bbox_width, 100), max(bbox_height, 100)))
                temp_draw = ImageDraw.Draw(temp_img)
                text_bbox = temp_draw.textbbox((0, 0), text, font=test_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # 同时考虑宽度和高度限制，选择更严格的约束
                width_fits = text_width <= target_width
                height_fits = text_height <= target_height
                
                if width_fits and height_fits:
                    best_size = mid_size
                    left = mid_size  # 尝试更大的字体
                else:
                    right = mid_size  # 字体太大，尝试更小的
                    
            except Exception as e:
                logger.warning(f"测试字体大小{mid_size}时出错：{str(e)}")
                right = mid_size
        
        # 最终验证和微调
        final_size = best_size
        try:
            if font_file_path:
                final_font = ImageFont.truetype(font_file_path, final_size)
            else:
                final_font = ImageFont.load_default()
                
            temp_img = Image.new('RGB', (max(bbox_width, 100), max(bbox_height, 100)))
            temp_draw = ImageDraw.Draw(temp_img)
            final_bbox = temp_draw.textbbox((0, 0), text, font=final_font)
            final_width = final_bbox[2] - final_bbox[0]
            final_height = final_bbox[3] - final_bbox[1]
            
            # 如果还有空间，尝试增大字体
            while final_size < max_size:
                test_size = final_size + 1
                if font_file_path:
                    test_font = ImageFont.truetype(font_file_path, test_size)
                else:
                    test_font = ImageFont.load_default()
                    
                test_bbox = temp_draw.textbbox((0, 0), text, font=test_font)
                test_width = test_bbox[2] - test_bbox[0]
                test_height = test_bbox[3] - test_bbox[1]
                
                if test_width <= target_width and test_height <= target_height:
                    final_size = test_size
                    final_width = test_width
                    final_height = test_height
                else:
                    break
                    
        except Exception as e:
            logger.warning(f"最终字体验证时出错：{str(e)}")
        
        # 确保字体大小在合理范围内
        final_size = max(min_size, min(final_size, max_size))
        
        logger.info(f"文字'{text[:10]}...'在bbox {bbox}(尺寸:{bbox_width}x{bbox_height})中，"
                   f"目标尺寸:{target_width}x{target_height}，最终字体大小：{final_size}")
        
        return final_size
    
    def parse_color(self, color_name):
        """解析颜色名称为RGB值"""
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "none": None
        }
        return color_map.get(color_name, (255, 0, 0))
    
    def calculate_text_position(self, bbox, text_size, position_mode):
        """根据边界框和位置模式计算文字位置"""
        x1, y1, x2, y2 = bbox
        text_width, text_height = text_size
        
        if position_mode == "bbox_top":
            # 在边界框上方
            return (x1, max(0, y1 - text_height - 5))
        elif position_mode == "bbox_bottom":
            # 在边界框下方
            return (x1, y2 + 5)
        elif position_mode == "bbox_center":
            # 在边界框中心
            center_x = x1 + (x2 - x1) // 2 - text_width // 2
            center_y = y1 + (y2 - y1) // 2 - text_height // 2
            return (center_x, center_y)
        elif position_mode == "bbox_left":
            # 在边界框左侧
            return (max(0, x1 - text_width - 5), y1)
        elif position_mode == "bbox_right":
            # 在边界框右侧
            return (x2 + 5, y1)
        else:
            # 默认在上方
            return (x1, max(0, y1 - text_height - 5))
    
    def draw_text_with_background(self, draw, position, text, font, text_color, bg_color, text_alpha, enable_stroke=True):
        """绘制带背景的文字"""
        x, y = position
        
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 绘制背景
        if bg_color is not None:
            padding = 2
            bg_bbox = [
                x - padding,
                y - padding,
                x + text_width + padding,
                y + text_height + padding
            ]
            draw.rectangle(bg_bbox, fill=bg_color)
        
        # 绘制文字
        if bg_color is None and enable_stroke:
            # 没有背景色且启用描边时，为文字添加描边以提高可读性
            stroke_color = (0, 0, 0) if sum(text_color) > 384 else (255, 255, 255)  # 根据文字颜色选择描边颜色
            stroke_width = max(1, font.size // 20)  # 根据字体大小调整描边宽度
            
            try:
                # 尝试使用stroke参数（PIL较新版本支持）
                draw.text((x, y), text, font=font, fill=text_color, 
                         stroke_width=stroke_width, stroke_fill=stroke_color)
            except TypeError:
                # 如果不支持stroke参数，使用传统方法绘制描边
                # 在周围绘制多个偏移的文字来模拟描边效果
                for dx in [-stroke_width, 0, stroke_width]:
                    for dy in [-stroke_width, 0, stroke_width]:
                        if dx != 0 or dy != 0:  # 跳过中心点
                            draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
                # 最后绘制主文字
                draw.text((x, y), text, font=font, fill=text_color)
        else:
            # 有背景色或禁用描边时，直接绘制文字
            draw.text((x, y), text, font=font, fill=text_color)
        
        return text_width, text_height
    
    def parse_ocr_json(self, ocr_json_str):
        """解析OCR JSON结果"""
        try:
            # 尝试直接解析JSON字符串
            if isinstance(ocr_json_str, str):
                # 如果是字符串，先尝试解析
                ocr_data = json.loads(ocr_json_str)
            else:
                ocr_data = ocr_json_str
            
            # 如果是完整的OCR结果格式
            if isinstance(ocr_data, dict) and "ocr_results" in ocr_data:
                ocr_results = ocr_data["ocr_results"]
            elif isinstance(ocr_data, list):
                # 如果直接是结果列表
                ocr_results = ocr_data
            else:
                logger.error("无法识别的OCR JSON格式")
                return []
            
            # 验证数据格式
            valid_results = []
            for item in ocr_results:
                if isinstance(item, dict) and "bbox_2d" in item and "text_content" in item:
                    bbox = item["bbox_2d"]
                    if len(bbox) >= 4:
                        valid_results.append(item)
            
            return valid_results
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败：{str(e)}")
            return []
        except Exception as e:
            logger.error(f"OCR数据解析失败：{str(e)}")
            return []
    
    def overlay_text(self, image, ocr_json, font_size_mode, font_size, fill_ratio, 
                    text_color, background_color, position_mode, enable_stroke, text_alpha=1.0, font_path=""):
        """在图片上叠加文字"""
        try:
            # 转换输入图像
            pil_image = self.tensor_to_pil(image)
            
            # 创建可绘制的图像副本
            overlay_image = pil_image.copy()
            draw = ImageDraw.Draw(overlay_image)
            
            # 解析OCR结果
            ocr_results = self.parse_ocr_json(ocr_json)
            if not ocr_results:
                logger.warning("没有找到有效的OCR结果")
                return (self.pil_to_tensor(overlay_image),)
            
            logger.info(f"准备绘制{len(ocr_results)}个文字项，模式：{font_size_mode}")
            
            # 解析颜色
            text_rgb = self.parse_color(text_color)
            bg_rgb = self.parse_color(background_color)
            
            # 绘制每个文字项
            for i, result in enumerate(ocr_results):
                try:
                    bbox = result["bbox_2d"][:4]  # 确保只取前4个坐标值
                    text_content = result["text_content"]
                    
                    if not text_content.strip():
                        continue
                    
                    # 根据模式决定字体大小
                    if font_size_mode == "auto_fit":
                        # 自动适应模式
                        actual_font_size = self.calculate_auto_font_size(
                            text_content, bbox, fill_ratio, font_path
                        )
                        font = self.get_font(actual_font_size, font_path)
                    elif font_size_mode == "max_fill":
                        # 最大化填充模式 - 使用99%填充率
                        actual_font_size = self.calculate_auto_font_size(
                            text_content, bbox, 0.99, font_path
                        )
                        font = self.get_font(actual_font_size, font_path)
                    else:
                        # 固定大小模式
                        font = self.get_font(font_size, font_path)
                        actual_font_size = font_size
                    
                    # 获取文字尺寸
                    text_bbox = draw.textbbox((0, 0), text_content, font=font)
                    text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])
                    
                    # 根据模式计算文字位置
                    if font_size_mode in ["auto_fit", "max_fill"]:
                        # 自动模式下，文字居中显示在bbox内
                        x1, y1, x2, y2 = bbox
                        center_x = x1 + (x2 - x1) // 2 - text_size[0] // 2
                        center_y = y1 + (y2 - y1) // 2 - text_size[1] // 2
                        text_position = (center_x, center_y)
                    else:
                        # 固定模式下，按照position_mode计算位置
                        text_position = self.calculate_text_position(bbox, text_size, position_mode)
                    
                    # 绘制文字
                    self.draw_text_with_background(
                        draw, text_position, text_content, font, 
                        text_rgb, bg_rgb, text_alpha, enable_stroke
                    )
                    
                    logger.info(f"已绘制文字 #{i+1}: '{text_content}' 字体大小:{actual_font_size} 位置:{text_position}")
                    
                except Exception as e:
                    logger.error(f"绘制第{i+1}个文字项时出错：{str(e)}")
                    continue
            
            # 转换回tensor并返回
            result_tensor = self.pil_to_tensor(overlay_image)
            return (result_tensor,)
            
        except Exception as e:
            error_msg = f"文字叠加处理失败：{str(e)}"
            logger.error(error_msg)
            
            # 发生错误时返回原图
            pil_image = self.tensor_to_pil(image)
            result_tensor = self.pil_to_tensor(pil_image)
            return (result_tensor,)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "TextOverlayNode": TextOverlayNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextOverlayNode": "文字叠加显示 (Text Overlay)"
}