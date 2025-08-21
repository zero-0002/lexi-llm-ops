# file: agent/nodes/planner.py

from langchain_core.runnables import Runnable
from agent.state import AgentState

class PlannerNode:
    """
    Một class chuyên dụng cho node planner.
    Nó đóng gói logic và các phụ thuộc cần thiết.
    """
    def __init__(self, llm_with_tools: Runnable):
        """
        Nhận LLM đã được bind tool khi khởi tạo.
        """
        self.llm_with_tools = llm_with_tools

    def __call__(self, state: AgentState) -> dict:
        """
        Logic thực thi của node khi được graph gọi.
        Python cho phép một instance của class được gọi như một hàm
        nếu nó có phương thức __call__.
        """
        messages = state["messages"]
        
        # Sử dụng LLM đã được lưu từ lúc khởi tạo
        response = self.llm_with_tools.invoke(messages)
        
        return {"messages": [response]}