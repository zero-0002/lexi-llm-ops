import json
import re
from typing import Dict, Any, List

def parse_mcp_tool(raw_tool_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuyển đổi cấu trúc tool thô từ MCP server thành định dạng JSON Schema
    thân thiện với LLM, giàu thông tin hơn.

    Args:
        raw_tool_data: Một dictionary chứa định nghĩa tool thô.

    Returns:
        Một dictionary với cấu trúc đã được tối ưu hóa.
    """
    # 1. Trích xuất thông tin cơ bản
    tool_name = raw_tool_data.get("name", "unknown_tool")
    raw_description = raw_tool_data.get("description", "")
    input_schema = raw_tool_data.get("inputSchema", {})
    
    # 2. Tách mô tả chính ra khỏi mô tả tham số
    # Lấy phần text trước dòng ":param" đầu tiên
    main_description = raw_description.split("\n\n:param")[0].strip()

    # 3. Xây dựng lại cấu trúc tham số (parameters)
    cleaned_properties = {}
    required_params = input_schema.get("required", [])
    
    # Tạo một dictionary để dễ dàng tra cứu mô tả tham số từ docstring
    param_descriptions = {}
    # Dùng regex để tìm tất cả các dòng :param name: description
    matches = re.findall(r":param\s+([^:]+):\s+(.+)", raw_description)
    for match in matches:
        param_name, desc = match
        param_descriptions[param_name.strip()] = desc.strip()

    # Lặp qua các thuộc tính trong inputSchema
    for param_name, param_info in input_schema.get("properties", {}).items():
        # Suy luận kiểu dữ liệu (bước này có thể cần tinh chỉnh)
        param_type = "string" # Mặc định
        if param_name in ["tail"]:
            param_type = "integer"
        elif param_info.get("default") is False or param_info.get("default") is True:
            param_type = "boolean"

        cleaned_properties[param_name] = {
            "type": param_type,
            # Lấy mô tả chi tiết từ docstring, nếu không có thì dùng title
            "description": param_descriptions.get(param_name, param_info.get("title", "")),
        }

    # 4. Lắp ráp lại thành cấu trúc JSON Schema cuối cùng
    final_tool_definition = {
        "name": tool_name,
        "description": main_description,
        "parameters": {
            "type": "object",
            "properties": cleaned_properties,
            "required": required_params
        }
    }
    
    return final_tool_definition

# --- DEMO SỬ DỤNG ---
if __name__ == "__main__":
    # Dữ liệu JSON gốc của tool k8s_logs
    k8s_logs_raw = {
        "name": "k8s_logs",
        "description": "Print the logs for a container in a pod.\n\n:param pod_name: The name of the pod.\n:param container: The name of the container in the pod. If not specified, uses the first container.\n:param namespace: The namespace of the pod. If not specified, uses the default namespace.\n:param tail: The number of lines from the end of the logs to show. If not specified, shows all lines.\n:param previous: Whether to show the logs for the previous instance of the container.\n:param since: Only return logs newer than a relative duration like 5s, 2m, or 3h, or an absolute timestamp.\n:param timestamps: Whether to include timestamps on each line.\n:param follow: Whether to follow the logs (stream in real-time).\n:return: The logs of the container.",
        "inputSchema": {
            "properties": {
                "pod_name": {"title": "Pod Name"},
                "container": {"default": None, "title": "Container"},
                "namespace": {"default": None, "title": "Namespace"},
                "tail": {"default": None, "title": "Tail"},
                "previous": {"default": False, "title": "Previous"},
                "since": {"default": None, "title": "Since"},
                "timestamps": {"default": False, "title": "Timestamps"},
                "follow": {"default": False, "title": "Follow"}
            },
            "required": ["pod_name"],
            "type": "object"
        }
    }

    # Chạy hàm để chuyển đổi
    cleaned_tool = parse_mcp_tool(k8s_logs_raw)

    # In ra kết quả JSON đã được tối ưu
    print(json.dumps(cleaned_tool, indent=2, ensure_ascii=False))