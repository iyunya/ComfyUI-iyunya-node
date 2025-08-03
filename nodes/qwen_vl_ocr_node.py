import os
import json
import base64
import logging
import requests
import numpy as np
import torch
from PIL import Image, ImageDraw
import cv2

logger = logging.getLogger("qwen_vl_ocr")

class QwenVLOCRNode:
    """
    阿里云百炼 Qwen-VL OCR 图片文字识别节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "阿里云百炼API Key，格式：sk-xxx"
                }),
                "custom_prompt": ("STRING", {
                    "default": "识别图片中的文字并翻译，附带标注box坐标，返回json {\"bbox_2d\":[x1,y1,x2,y2],\"text_content\":\"翻译内容\"}",
                    "multiline": True,
                    "tooltip": "自定义识别提示词"
                }),
                "model": (["qwen-vl-max-latest", "qwen-vl-max", "qwen-vl-plus-latest", "qwen-vl-plus"], {
                    "default": "qwen-vl-max-latest"
                })
            },
            "optional": {
                "api_base_url": ("STRING", {
                    "default": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "multiline": False,
                    "tooltip": "API基础URL"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("marked_image", "text_mask", "ocr_result_json")
    FUNCTION = "process_ocr"
    CATEGORY = "iyunya/文字识别"
    
    def tensor_to_pil(self, tensor):
        """将tensor转换为PIL图像"""
        # tensor shape: [batch, height, width, channels]
        if len(tensor.shape) == 4:
            tensor = tensor[0]  # 取第一张图片
        
        # 转换为numpy并调整数据类型
        image_np = tensor.cpu().numpy()
        if image_np.max() <= 1.0:
            image_np = (image_np * 255).astype(np.uint8)
        else:
            image_np = image_np.astype(np.uint8)
            
        return Image.fromarray(image_np)
    
    def pil_to_tensor(self, pil_image):
        """将PIL图像转换为tensor"""
        image_np = np.array(pil_image).astype(np.float32) / 255.0
        return torch.from_numpy(image_np).unsqueeze(0)  # 添加batch维度
    
    def image_to_base64(self, pil_image):
        """将PIL图像转换为base64编码"""
        import io
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    
    def call_qwen_vl_api(self, image_base64, prompt, api_key, model, api_base_url):
        """调用阿里云百炼Qwen-VL API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "你是一个专业的OCR文字识别助手，请准确识别图片中的文字内容。"}]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_base64}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                logger.info(f"API调用成功，返回内容：{content}")
                return content
            else:
                raise Exception(f"API返回格式错误：{result}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败：{str(e)}")
            raise Exception(f"API请求失败：{str(e)}")
        except Exception as e:
            logger.error(f"处理API响应时出错：{str(e)}")
            raise Exception(f"处理API响应时出错：{str(e)}")
    
    def parse_ocr_result(self, content):
        """解析OCR结果，提取JSON格式的文本和坐标信息"""
        ocr_results = []
        
        try:
            # 先清理内容，去除markdown代码块标记
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # 去除 ```json
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # 去除 ```
            cleaned_content = cleaned_content.strip()
            
            # 尝试直接解析JSON
            if cleaned_content.startswith('{') or cleaned_content.startswith('['):
                data = json.loads(cleaned_content)
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    if 'bbox_2d' in item and 'text_content' in item:
                        ocr_results.append(item)
            else:
                # 尝试从文本中提取JSON块
                import re
                # 更宽松的JSON匹配模式
                json_pattern = r'\{[^{}]*"bbox_2d"[^{}]*"text_content"[^{}]*\}'
                matches = re.findall(json_pattern, cleaned_content, re.DOTALL)
                
                for match in matches:
                    try:
                        data = json.loads(match)
                        ocr_results.append(data)
                    except json.JSONDecodeError:
                        continue
                
                # 如果没有找到标准格式，尝试从整个文本中提取
                if not ocr_results:
                    # 查找坐标模式 [x1,y1,x2,y2] 或类似格式
                    coord_pattern = r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'
                    coords = re.findall(coord_pattern, cleaned_content)
                    
                    if coords:
                        # 简单假设：如果找到坐标，就把整个内容作为文本
                        for i, coord in enumerate(coords):
                            x1, y1, x2, y2 = map(int, coord)
                            ocr_results.append({
                                "bbox_2d": [x1, y1, x2, y2],
                                "text_content": f"文字区域{i+1}"  # 使用简单的区域标识
                            })
                    else:
                        # 如果完全没有坐标信息，创建一个默认结果
                        ocr_results.append({
                            "bbox_2d": [0, 0, 100, 50],
                            "text_content": "识别结果"
                        })
            
        except Exception as e:
            logger.warning(f"解析OCR结果时出错：{str(e)}，使用默认格式")
            # 返回默认结果
            ocr_results.append({
                "bbox_2d": [0, 0, 100, 50],
                "text_content": "解析失败"
            })
        
        return ocr_results
    
    def draw_bboxes_on_image(self, pil_image, ocr_results):
        """在图片上绘制边界框"""
        draw_image = pil_image.copy()
        draw = ImageDraw.Draw(draw_image)
        
        for i, result in enumerate(ocr_results):
            bbox = result.get("bbox_2d", [0, 0, 100, 50])
            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[:4]
                # 绘制红色边界框
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                
                # 绘制序号而不是中文文字，避免编码问题
                try:
                    if y1 > 20:  # 确保有足够空间绘制序号
                        # 绘制序号标识
                        draw.text((x1, y1-20), f"#{i+1}", fill="red")
                except Exception as e:
                    # 如果绘制出现任何问题，只记录警告，继续绘制边界框
                    logger.warning(f"绘制序号时出现错误：{str(e)}")
        
        return draw_image
    
    def create_mask_from_bboxes(self, image_size, ocr_results):
        """根据边界框创建mask"""
        width, height = image_size
        mask = Image.new('L', (width, height), 0)  # 黑色背景
        draw = ImageDraw.Draw(mask)
        
        for result in ocr_results:
            bbox = result.get("bbox_2d", [0, 0, 100, 50])
            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[:4]
                # 在mask上绘制白色矩形
                draw.rectangle([x1, y1, x2, y2], fill=255)
        
        return mask
    
    def process_ocr(self, image, api_key, custom_prompt, model, api_base_url=None):
        """处理OCR识别"""
        if not api_key or not api_key.strip():
            raise ValueError("请提供有效的阿里云百炼API Key")
        
        if api_base_url is None:
            api_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        try:
            # 转换输入图像
            pil_image = self.tensor_to_pil(image)
            logger.info(f"图像尺寸：{pil_image.size}")
            
            # 转换为base64
            image_base64 = self.image_to_base64(pil_image)
            
            # 调用API
            logger.info("正在调用阿里云百炼API...")
            api_result = self.call_qwen_vl_api(
                image_base64, custom_prompt, api_key, model, api_base_url
            )
            
            # 解析结果
            ocr_results = self.parse_ocr_result(api_result)
            logger.info(f"解析到{len(ocr_results)}个文字区域")
            
            # 在图像上绘制边界框
            marked_image = self.draw_bboxes_on_image(pil_image, ocr_results)
            
            # 创建mask
            mask_image = self.create_mask_from_bboxes(pil_image.size, ocr_results)
            
            # 准备返回的JSON结果，确保UTF-8编码
            result_json = {
                "status": "success",
                "model_used": model,
                "ocr_results": ocr_results,
                "total_detections": len(ocr_results),
                "original_response": api_result
            }
            
            # 转换回tensor格式
            marked_tensor = self.pil_to_tensor(marked_image)
            mask_tensor = self.pil_to_tensor(mask_image)
            
            # 确保JSON序列化时使用UTF-8编码
            json_result = json.dumps(result_json, ensure_ascii=False, indent=2)
            
            return (marked_tensor, mask_tensor, json_result)
            
        except Exception as e:
            error_msg = f"OCR处理失败：{str(e)}"
            logger.error(error_msg)
            
            # 返回错误信息
            error_result = {
                "status": "error",
                "error_message": str(e),
                "ocr_results": [],
                "total_detections": 0
            }
            
            # 返回原图和空mask
            pil_image = self.tensor_to_pil(image)
            empty_mask = Image.new('L', pil_image.size, 0)
            
            marked_tensor = self.pil_to_tensor(pil_image)
            mask_tensor = self.pil_to_tensor(empty_mask)
            
            json_result = json.dumps(error_result, ensure_ascii=False, indent=2)
            
            return (marked_tensor, mask_tensor, json_result)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "QwenVLOCRNode": QwenVLOCRNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenVLOCRNode": "阿里云百炼文字识别 (Qwen-VL OCR)"
} 