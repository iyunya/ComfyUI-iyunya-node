import os
import json
from aiohttp import web
import uuid
import logging
from server import PromptServer
# 导入主节点映射
import nodes as comfy_nodes


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iyunya_nodes")

# 全局存储所有动态创建的节点
DYNAMIC_NODE_CLASSES = {}
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 节点配置保存路径
NODES_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_in_nodes")
os.makedirs(NODES_CONFIG_DIR, exist_ok=True)


class IyunyaInNode:
    """
    动态创建的输入节点，具有可配置的输入和输出
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 从类属性获取动态输入类型
        return cls._input_types if hasattr(cls, "_input_types") else {"required": {}}
    
    # 这些属性将在运行时动态设置
    FUNCTION = "execute"
    CATEGORY = "iyunya/in"
    
    def __init__(self):
        pass
    
    def execute(self, **kwargs):
        # 使用kwargs中的所有输入值作为输出
        # 输出顺序基于RETURN_NAMES
        result = []
        for name in self.RETURN_NAMES:
            if name in kwargs:
                result.append(kwargs[name])
            else:
                # 如果输入中没有对应的值，提供一个默认值
                # 基于输出类型
                type_idx = self.RETURN_NAMES.index(name)
                if type_idx < len(self.RETURN_TYPES):
                    return_type = self.RETURN_TYPES[type_idx]
                    result.append(get_default_value_for_type(return_type))
                else:
                    result.append(None)
        
        return tuple(result)


def get_default_value_for_type(type_name):
    """为不同类型返回默认值"""
    type_defaults = {
        "STRING": "",
        "INT": 0,
        "FLOAT": 0.0,
        "BOOLEAN": False,
        "COMBO": "",
    }
    return type_defaults.get(type_name, None)


def save_node_config(node_id, config):
    """保存节点配置到磁盘"""
    try:
        config_path = os.path.join(NODES_CONFIG_DIR, f"{node_id}.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存节点配置失败: {str(e)}")
        return False


def load_node_config(node_id):
    """从磁盘加载节点配置"""
    try:
        config_path = os.path.join(NODES_CONFIG_DIR, f"{node_id}.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载节点配置失败: {str(e)}")
    return None


def delete_node_config(node_id):
    """从磁盘删除节点配置"""
    try:
        config_path = os.path.join(NODES_CONFIG_DIR, f"{node_id}.json")
        if os.path.exists(config_path):
            os.remove(config_path)
        return True
    except Exception as e:
        print(f"删除节点配置失败: {str(e)}")
        return False


def create_dynamic_node(config, save_to_disk=True):
    """
    基于配置创建一个新的动态节点类
    
    config = {
        "id": "unique_id",
        "inputs": {
            "param1": "STRING",
            "param2": "INT",
            ...
        },
        "name": "自定义节点名称"  # 可选
    }
    """
    # 生成一个唯一的类名
    node_id = config.get("id", f"iyunya_in_{uuid.uuid4().hex[:8]}")
    class_name = f"iyunya_in_{node_id}"
    
    # 准备输入类型
    input_types = {"required": {}}
    for param_name, param_type in config.get("inputs", {}).items():
        if param_type == "STRING":
            input_types["required"][param_name] = ("STRING", {"multiline": False, "default": ""})
        elif param_type == "INT":
            input_types["required"][param_name] = ("INT", {"default": 0, "min": -2147483648, "max": 2147483647})
        elif param_type == "FLOAT":
            input_types["required"][param_name] = ("FLOAT", {"default": 0.0, "min": -3.402823e+38, "max": 3.402823e+38})
        elif param_type == "BOOLEAN":
            input_types["required"][param_name] = (["True", "False"], {"default": "False"})
        else:
            # 默认作为字符串处理
            input_types["required"][param_name] = ("STRING", {"multiline": False, "default": ""})
    
    # 创建新类
    DynamicNodeClass = type(class_name, (IyunyaInNode,), {
        "_input_types": input_types,
        "RETURN_TYPES": tuple(config.get("inputs", {}).values()),
        "RETURN_NAMES": tuple(config.get("inputs", {}).keys()),
    })
    
    # 保存节点类
    DYNAMIC_NODE_CLASSES[node_id] = DynamicNodeClass
    
    # 注册节点
    node_name = f"iyunya_in_{node_id}"
    display_name = config.get("name", f"工作流输入 {node_id}")
    
    # 添加到本地映射
    NODE_CLASS_MAPPINGS[node_name] = DynamicNodeClass
    NODE_DISPLAY_NAME_MAPPINGS[node_name] = display_name
    
    # 同时添加到ComfyUI主节点映射，确保能被/api/object_info识别
    comfy_nodes.NODE_CLASS_MAPPINGS[node_name] = DynamicNodeClass
    comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS[node_name] = display_name
    
    # 保存配置到磁盘
    if save_to_disk:
        save_node_config(node_id, config)
    
    logger.info(f"创建节点成功: {display_name} (ID: {node_id})")
    
    return {
        "id": node_id,
        "class_name": class_name,
        "node_name": node_name,
        "display_name": display_name
    }


def remove_dynamic_node(node_id, delete_from_disk=True):
    """删除一个动态节点"""
    node_name = f"iyunya_in_{node_id}"
    
    # 检查节点是否存在
    node_exists = (node_name in NODE_CLASS_MAPPINGS or 
                   node_name in comfy_nodes.NODE_CLASS_MAPPINGS or 
                   node_id in DYNAMIC_NODE_CLASSES)
    
    if not node_exists:
        logger.warning(f"尝试删除不存在的节点: {node_id}")
        return False
    
    # 获取节点名称用于日志
    display_name = NODE_DISPLAY_NAME_MAPPINGS.get(node_name, f"未知节点 ({node_id})")
    
    # 从本地映射中删除
    if node_name in NODE_CLASS_MAPPINGS:
        del NODE_CLASS_MAPPINGS[node_name]
    
    if node_name in NODE_DISPLAY_NAME_MAPPINGS:
        del NODE_DISPLAY_NAME_MAPPINGS[node_name]
    
    # 从ComfyUI主节点映射中删除
    if node_name in comfy_nodes.NODE_CLASS_MAPPINGS:
        del comfy_nodes.NODE_CLASS_MAPPINGS[node_name]
    
    if node_name in comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS:
        del comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS[node_name]
    
    if node_id in DYNAMIC_NODE_CLASSES:
        del DYNAMIC_NODE_CLASSES[node_id]
    
    # 从磁盘删除配置
    if delete_from_disk:
        delete_node_config(node_id)
    
    logger.info(f"删除节点成功: {display_name} (ID: {node_id})")
    
    return True


def load_all_saved_nodes():
    """加载所有保存的节点配置"""
    try:
        if not os.path.exists(NODES_CONFIG_DIR):
            return

        loaded_count = 0
        for filename in os.listdir(NODES_CONFIG_DIR):
            if filename.endswith('.json'):
                node_id = os.path.splitext(filename)[0]
                config = load_node_config(node_id)
                if config:
                    create_dynamic_node(config, save_to_disk=False)  # 不重复保存
                    loaded_count += 1
        
        logger.info(f"已加载 {loaded_count} 个持久化动态节点")
    except Exception as e:
        logger.error(f"加载保存的节点时出错: {str(e)}")


# 添加API路由处理函数
@PromptServer.instance.routes.post("/api/iyunya/in")
async def api_create_iyunya_in(request):
    try:
        data = await request.json()
        
        # 准备节点配置
        config = {
            "id": data.get("id", uuid.uuid4().hex[:8]),
            "inputs": data.get("inputs", {}),
            "name": data.get("name", "动态输入节点")
        }
        
        logger.info(f"收到创建节点请求: {config['name']}")
        
        # 创建节点
        result = create_dynamic_node(config)
        
        # 返回创建结果
        return web.json_response({
            "status": "success",
            "node": result
        })
    
    except Exception as e:
        import traceback
        logger.error(f"创建节点失败: {str(e)}\n{traceback.format_exc()}")
        return web.json_response({
            "status": "failed",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@PromptServer.instance.routes.get("/api/iyunya/in/{node_id}")
async def api_get_iyunya_in(request):
    try:
        node_id = request.match_info.get("node_id")
        node_name = f"iyunya_in_{node_id}"
        
        logger.info(f"请求节点信息: {node_id}")
        
        if node_name not in NODE_CLASS_MAPPINGS:
            logger.warning(f"找不到节点: {node_id}")
            return web.json_response({
                "status": "failed",
                "message": f"Node with ID {node_id} not found"
            }, status=404)
        
        node_class = NODE_CLASS_MAPPINGS[node_name]
        
        # 获取节点信息
        return web.json_response({
            "status": "success",
            "node": {
                "id": node_id,
                "class_name": node_class.__name__,
                "node_name": node_name,
                "display_name": NODE_DISPLAY_NAME_MAPPINGS[node_name],
                "return_types": node_class.RETURN_TYPES,
                "return_names": node_class.RETURN_NAMES,
                "input_types": node_class.INPUT_TYPES()
            }
        })
    
    except Exception as e:
        import traceback
        logger.error(f"获取节点信息失败: {str(e)}\n{traceback.format_exc()}")
        return web.json_response({
            "status": "failed",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@PromptServer.instance.routes.post("/api/iyunya/in/delete")
async def api_delete_iyunya_in(request):
    try:
        data = await request.json()
        node_id = data.get("id")
        
        logger.info(f"收到删除节点请求: {node_id}")
        
        if not node_id:
            logger.warning("删除节点请求中未提供节点ID")
            return web.json_response({
                "status": "failed",
                "message": "Node ID is required"
            }, status=400)
        
        # 尝试删除节点
        success = remove_dynamic_node(node_id)
        
        if success:
            return web.json_response({
                "status": "success",
                "message": f"Node with ID {node_id} removed"
            })
        else:
            logger.warning(f"删除不存在的节点: {node_id}")
            return web.json_response({
                "status": "failed",
                "message": f"Failed to remove node with ID {node_id}"
            }, status=400)
    
    except Exception as e:
        import traceback
        logger.error(f"删除节点失败: {str(e)}\n{traceback.format_exc()}")
        return web.json_response({
            "status": "failed",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@PromptServer.instance.routes.get("/api/iyunya/in/list")
async def api_list_iyunya_in(request):
    try:
        logger.info("请求节点列表")
        
        # 列出所有动态节点
        nodes = []
        for node_id, node_class in DYNAMIC_NODE_CLASSES.items():
            node_name = f"iyunya_in_{node_id}"
            nodes.append({
                "id": node_id,
                "class_name": node_class.__name__,
                "node_name": node_name,
                "display_name": NODE_DISPLAY_NAME_MAPPINGS.get(node_name, "Unknown"),
                "return_types": node_class.RETURN_TYPES,
                "return_names": node_class.RETURN_NAMES
            })
        
        logger.info(f"返回节点列表，共 {len(nodes)} 个节点")
        
        return web.json_response({
            "status": "success",
            "nodes": nodes
        })
    
    except Exception as e:
        import traceback
        logger.error(f"获取节点列表失败: {str(e)}\n{traceback.format_exc()}")
        return web.json_response({
            "status": "failed",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


# 创建默认节点
default_node_config = {
    "id": "default",
    "inputs": {
        "text": "STRING", 
        "number": "INT",
        "flag": "BOOLEAN"
    },
    "name": "DemoInputNode"
}

# 加载所有保存的节点配置
load_all_saved_nodes()

# 确保默认节点存在（如果不存在则创建）
if "default" not in DYNAMIC_NODE_CLASSES:
    create_dynamic_node(default_node_config)