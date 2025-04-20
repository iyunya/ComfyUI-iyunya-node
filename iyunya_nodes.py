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
NODES_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_nodes")
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
    CATEGORY = "工作流/输入"
    
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


class IyunyaOutNode:
    """
    动态创建的输出节点，用于接收和处理工作流中的输出
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 从类属性获取动态输入类型
        return cls._input_types if hasattr(cls, "_input_types") else {"required": {}}
    
    # 这些属性将在运行时动态设置
    FUNCTION = "execute"
    CATEGORY = "工作流/输出"
    OUTPUT_NODE = True  # 标记为输出节点，确保它的输入会被执行
    
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
        # 确保组目录存在
        group = config.get("group", "in")
        group_dir = os.path.join(NODES_CONFIG_DIR, group)
        os.makedirs(group_dir, exist_ok=True)
        
        config_path = os.path.join(group_dir, f"{node_id}.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存节点配置失败: {str(e)}")
        return False


def load_node_config(node_id, group="in"):
    """从磁盘加载节点配置"""
    try:
        config_path = os.path.join(NODES_CONFIG_DIR, group, f"{node_id}.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载节点配置失败: {str(e)}")
    return None


def delete_node_config(node_id, group="in"):
    """从磁盘删除节点配置"""
    try:
        config_path = os.path.join(NODES_CONFIG_DIR, group, f"{node_id}.json")
        if os.path.exists(config_path):
            os.remove(config_path)
        return True
    except Exception as e:
        logger.error(f"删除节点配置失败: {str(e)}")
        return False


def create_dynamic_node(config, save_to_disk=True):
    """
    基于配置创建一个新的动态节点类
    
    config = {
        "id": "unique_id",
        "group": "in" 或 "out",  # 节点类型组
        "inputs": {             # 对于in节点是输入参数，对于out节点是需要接收的数据
            "param1": "STRING",
            "param2": "INT",
            ...
        },
        "name": "自定义节点名称"  # 可选
    }
    """
    # 确定节点组和类型
    group = config.get("group", "in")
    if group not in ["in", "out"]:
        raise ValueError(f"不支持的节点组类型: {group}，只支持 'in' 或 'out'")
    
    # 生成一个唯一的类名和ID
    node_id = config.get("id", f"iyunya_{group}_{uuid.uuid4().hex[:8]}")
    class_name = f"iyunya_{group}_{node_id}"
    
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
    
    # 基于组类型创建相应的节点类
    if group == "in":
        DynamicNodeClass = type(class_name, (IyunyaInNode,), {
            "_input_types": input_types,
            "RETURN_TYPES": tuple(config.get("inputs", {}).values()),
            "RETURN_NAMES": tuple(config.get("inputs", {}).keys()),
        })
    else:  # out
        DynamicNodeClass = type(class_name, (IyunyaOutNode,), {
            "_input_types": input_types,
            "RETURN_TYPES": tuple(config.get("inputs", {}).values()),
            "RETURN_NAMES": tuple(config.get("inputs", {}).keys()),
        })
    
    # 保存节点类到对应组
    if group not in DYNAMIC_NODE_CLASSES:
        DYNAMIC_NODE_CLASSES[group] = {}
    DYNAMIC_NODE_CLASSES[group][node_id] = DynamicNodeClass
    
    # 注册节点
    node_name = f"iyunya_{group}_{node_id}"
    display_name = config.get("name", f"工作流{group == 'in' and '输入' or '输出'} {node_id}")
    
    # 添加到本地映射
    NODE_CLASS_MAPPINGS[node_name] = DynamicNodeClass
    NODE_DISPLAY_NAME_MAPPINGS[node_name] = display_name
    
    # 同时添加到ComfyUI主节点映射，确保能被/api/object_info识别
    comfy_nodes.NODE_CLASS_MAPPINGS[node_name] = DynamicNodeClass
    comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS[node_name] = display_name
    
    # 保存配置到磁盘
    if save_to_disk:
        save_node_config(node_id, config)
    
    logger.info(f"创建节点成功: {display_name} (ID: {node_id}, 组: {group})")
    
    return {
        "id": node_id,
        "group": group,
        "class_name": class_name,
        "node_name": node_name,
        "display_name": display_name
    }


def remove_dynamic_node(node_id, group="in"):
    """删除一个动态节点"""
    node_name = f"iyunya_{group}_{node_id}"
    
    # 检查节点是否存在
    node_exists = (node_name in NODE_CLASS_MAPPINGS or 
                   node_name in comfy_nodes.NODE_CLASS_MAPPINGS or 
                   (group in DYNAMIC_NODE_CLASSES and node_id in DYNAMIC_NODE_CLASSES[group]))
    
    if not node_exists:
        logger.warning(f"尝试删除不存在的节点: {node_id} (组: {group})")
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
    
    # 从动态节点类映射中删除
    if group in DYNAMIC_NODE_CLASSES and node_id in DYNAMIC_NODE_CLASSES[group]:
        del DYNAMIC_NODE_CLASSES[group][node_id]
    
    # 从磁盘删除配置
    delete_node_config(node_id, group)
    
    logger.info(f"删除节点成功: {display_name} (ID: {node_id}, 组: {group})")
    
    return True


def load_all_saved_nodes():
    """加载所有保存的节点配置"""
    try:
        if not os.path.exists(NODES_CONFIG_DIR):
            return

        loaded_count = 0
        # 加载所有组下的节点
        for group in ["in", "out"]:
            group_dir = os.path.join(NODES_CONFIG_DIR, group)
            if os.path.exists(group_dir):
                for filename in os.listdir(group_dir):
                    if filename.endswith('.json'):
                        node_id = os.path.splitext(filename)[0]
                        config = load_node_config(node_id, group)
                        if config:
                            create_dynamic_node(config, save_to_disk=False)  # 不重复保存
                            loaded_count += 1
        
        logger.info(f"已加载 {loaded_count} 个持久化动态节点")
    except Exception as e:
        logger.error(f"加载保存的节点时出错: {str(e)}")


# API路由处理函数
@PromptServer.instance.routes.post("/api/iyunya/node/create")
async def api_create_iyunya_node(request):
    try:
        data = await request.json()
        
        # 准备节点配置
        group = data.get("group", "in")
        if group not in ["in", "out"]:
            return web.json_response({
                "status": "failed", 
                "message": f"不支持的节点组类型: {group}，只支持 'in' 或 'out'"
            }, status=400)
        
        config = {
            "id": data.get("id", uuid.uuid4().hex[:8]),
            "group": group,
            "inputs": data.get("inputs", {}),
            "name": data.get("name", f"动态{group == 'in' and '输入' or '输出'}节点")
        }
        
        logger.info(f"收到创建节点请求: {config['name']} (组: {group})")
        
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


@PromptServer.instance.routes.get("/api/iyunya/node/{node_id}")
async def api_get_iyunya_node(request):
    try:
        node_id = request.match_info.get("node_id")
        group = request.query.get("group", "in")
        if group not in ["in", "out"]:
            return web.json_response({
                "status": "failed", 
                "message": f"不支持的节点组类型: {group}，只支持 'in' 或 'out'"
            }, status=400)
            
        node_name = f"iyunya_{group}_{node_id}"
        
        logger.info(f"请求节点信息: {node_id} (组: {group})")
        
        if node_name not in NODE_CLASS_MAPPINGS:
            logger.warning(f"找不到节点: {node_id} (组: {group})")
            return web.json_response({
                "status": "failed",
                "message": f"Node with ID {node_id} in group {group} not found"
            }, status=404)
        
        node_class = NODE_CLASS_MAPPINGS[node_name]
        
        # 获取节点信息
        node_info = {
            "id": node_id,
            "group": group,
            "class_name": node_class.__name__,
            "node_name": node_name,
            "display_name": NODE_DISPLAY_NAME_MAPPINGS[node_name],
            "input_types": node_class.INPUT_TYPES()
        }
        
        # in类型的节点需要返回输出信息
        if hasattr(node_class, "RETURN_TYPES") and hasattr(node_class, "RETURN_NAMES"):
            node_info["return_types"] = node_class.RETURN_TYPES
            node_info["return_names"] = node_class.RETURN_NAMES
        
        return web.json_response({
            "status": "success",
            "node": node_info
        })
    
    except Exception as e:
        import traceback
        logger.error(f"获取节点信息失败: {str(e)}\n{traceback.format_exc()}")
        return web.json_response({
            "status": "failed",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@PromptServer.instance.routes.post("/api/iyunya/node/delete")
async def api_delete_iyunya_node(request):
    try:
        data = await request.json()
        node_id = data.get("id")
        group = data.get("group", "in")
        
        if group not in ["in", "out"]:
            return web.json_response({
                "status": "failed", 
                "message": f"不支持的节点组类型: {group}，只支持 'in' 或 'out'"
            }, status=400)
        
        logger.info(f"收到删除节点请求: {node_id} (组: {group})")
        
        if not node_id:
            logger.warning("删除节点请求中未提供节点ID")
            return web.json_response({
                "status": "failed",
                "message": "Node ID is required"
            }, status=400)
        
        # 尝试删除节点
        success = remove_dynamic_node(node_id, group)
        
        if success:
            return web.json_response({
                "status": "success",
                "message": f"Node with ID {node_id} in group {group} removed"
            })
        else:
            logger.warning(f"删除不存在的节点: {node_id} (组: {group})")
            return web.json_response({
                "status": "failed",
                "message": f"Failed to remove node with ID {node_id} in group {group}"
            }, status=400)
    
    except Exception as e:
        import traceback
        logger.error(f"删除节点失败: {str(e)}\n{traceback.format_exc()}")
        return web.json_response({
            "status": "failed",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@PromptServer.instance.routes.get("/api/iyunya/node/list")
async def api_list_iyunya_nodes(request):
    try:
        group = request.query.get("group", None)
        
        logger.info(f"请求节点列表{group and '（组: ' + group + '）' or ''}")
        
        # 列出指定组或所有组的动态节点
        nodes = []
        
        # 如果指定了组，只查找该组
        if group is not None:
            if group not in ["in", "out"]:
                return web.json_response({
                    "status": "failed", 
                    "message": f"不支持的节点组类型: {group}，只支持 'in' 或 'out'"
                }, status=400)
                
            if group in DYNAMIC_NODE_CLASSES:
                for node_id, node_class in DYNAMIC_NODE_CLASSES[group].items():
                    node_name = f"iyunya_{group}_{node_id}"
                    node_info = {
                        "id": node_id,
                        "group": group,
                        "class_name": node_class.__name__,
                        "node_name": node_name,
                        "display_name": NODE_DISPLAY_NAME_MAPPINGS.get(node_name, "Unknown"),
                    }
                    
                    # in类型的节点需要返回输出信息
                    if hasattr(node_class, "RETURN_TYPES") and hasattr(node_class, "RETURN_NAMES"):
                        node_info["return_types"] = node_class.RETURN_TYPES
                        node_info["return_names"] = node_class.RETURN_NAMES
                        
                    nodes.append(node_info)
        else:
            # 查找所有组
            for group_name, group_nodes in DYNAMIC_NODE_CLASSES.items():
                for node_id, node_class in group_nodes.items():
                    node_name = f"iyunya_{group_name}_{node_id}"
                    node_info = {
                        "id": node_id,
                        "group": group_name,
                        "class_name": node_class.__name__,
                        "node_name": node_name,
                        "display_name": NODE_DISPLAY_NAME_MAPPINGS.get(node_name, "Unknown"),
                    }
                    
                    # in类型的节点需要返回输出信息
                    if hasattr(node_class, "RETURN_TYPES") and hasattr(node_class, "RETURN_NAMES"):
                        node_info["return_types"] = node_class.RETURN_TYPES
                        node_info["return_names"] = node_class.RETURN_NAMES
                        
                    nodes.append(node_info)
        
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
default_in_node_config = {
    "id": "default",
    "group": "in",
    "inputs": {
        "text": "STRING", 
        "number": "INT",
        "flag": "BOOLEAN"
    },
    "name": "示例输入节点"
}

default_out_node_config = {
    "id": "default",
    "group": "out",
    "inputs": {
        "output_text": "STRING", 
        "output_number": "INT",
        "output_flag": "BOOLEAN"
    },
    "name": "示例输出节点"
}

# 加载所有保存的节点配置
load_all_saved_nodes()

# 确保默认节点存在（如果不存在则创建）
if "in" not in DYNAMIC_NODE_CLASSES or "default" not in DYNAMIC_NODE_CLASSES.get("in", {}):
    create_dynamic_node(default_in_node_config)

if "out" not in DYNAMIC_NODE_CLASSES or "default" not in DYNAMIC_NODE_CLASSES.get("out", {}):
    create_dynamic_node(default_out_node_config)