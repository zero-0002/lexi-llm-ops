from typing import List, Dict, Any, TypedDict, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # Input từ người dùng
    input: str
    
    # Lịch sử messages để tracking workflow
    messages: List[BaseMessage]
    
    # Plan được tạo ra từ planner
    plan: Optional[Dict[str, Any]]
    
    # Tools results
    tool_results: List[Dict[str, Any]]
    
    # Response cuối cùng
    final_response: str
    
    # Trạng thái hiện tại của workflow
    current_step: str